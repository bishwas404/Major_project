import ast
import json
import random
from io import BytesIO
import PyPDF2
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.modules.duplicate_removal import (
    remove_distractors_duplicate_with_correct_answer,
    remove_duplicates,
)
from apps.modules.keyword_chunking import keyword_centric_chunking
from apps.modules.text_clean import clean_text

from .forms import InputForm
from .models import MCQ


def generate_mcq(request):
    if request.method == "POST":
        form = InputForm(request.POST, request.FILES)
        print(form.errors)  #viewing any errors in input form
        if form.is_valid():
            context = clean_text(form.cleaned_data["context"]).strip()
            pdfile=form.cleaned_data["pdf_file"]
            num_keywords = int(form.cleaned_data["num_keywords"])
            option_1 = form.cleaned_data["option_1"]
            option_2 = form.cleaned_data["option_2"]
            option_3 = form.cleaned_data["option_3"]
            
            print(f"Raw POST Data: {request.POST}")  # Debugging purpose
            if not context and pdfile:    # if pdf file is present but no context input
                    print("trying to read the file")
                    reader=PyPDF2.PdfReader(pdfile,strict=False)
                    context=""
                    for page in reader.pages:
                        context+=page.extract_text() or ""   #appending each extracted page texts in pdf file to context string.
            print("reading completed!")   
            # Step 1: Quick Character-Length Check (~2500 chars ≈ 500 tokens)
            if len(context) > 2500:
                from apps.questionGeneration import question_tokenizer
                tokenized_length = len(question_tokenizer.tokenize(context))
            else:
                tokenized_length = 0  # Skip full tokenization if unlikely to exceed limit

            # Step 2: If Tokens > 500, Apply Keyword-Centric Chunking
            if tokenized_length > 500:
                chunks = keyword_centric_chunking(context, question_tokenizer)
            else:
                chunks = [context]

            # Step 3: Process Each Chunk Separately
            all_keywords = []
            questions_dict, distractors_dict = {}, {}

            for chunk in chunks:
                keywords = extract_keywords_based_on_option(option_2, chunk, num_keywords)
                keywords = remove_duplicates(keywords)
                all_keywords.extend(keywords)

                q_dict, d_dict = generate_questions_and_distractors(option_1, option_3, chunk, keywords)
                questions_dict.update(q_dict)
                distractors_dict.update(d_dict)

            # Step 4: Apply Duplicate Removal for Distractors
            for keyword in all_keywords:
                distractors_dict[keyword] = remove_distractors_duplicate_with_correct_answer(keyword, distractors_dict[keyword])

            # Step 5: Prepare MCQs
            mcq_list = create_mcq_list(all_keywords, questions_dict, distractors_dict)

            if request.user.is_authenticated:
                MCQ.objects.create(user=request.user, mcqs=json.dumps(mcq_list))  # Store in DB
            else:
                request.session.pop('mcqs', None)
                request.session['mcqs'] = json.dumps(mcq_list)  # Store in session

            return render(request, "quesGens/result.html", {"context": context, "mcq_list": mcq_list})
        
    return render(request, "quesGens/index.html", {"form": InputForm(), 'user': request.user if request.user.is_authenticated else None})

def result(request):
    if request.user.is_authenticated:
        latest_batch = MCQ.objects.latest('created_at')  # Fetch latest MCQs from DB
        mcq_list = json.loads(latest_batch.mcqs)
        mcq_list = ast.literal_eval(mcq_list)  # Convert to Python list
    else:
        mcq_list = request.session.get('mcqs', None)
        if mcq_list is not None:
            mcq_list = json.loads(mcq_list)
        else:
            mcq_list = []
    
    return render(request, 'quesGens/result.html', {"mcq_list": mcq_list})


def download_pdf(request):
    mcq_list = request.session.get('mcq_list')
    
    # Check if mcq_list is available
    if not mcq_list:
        return render(request, "quesGens/error.html", 
                      {"error": "No MCQs found to download as PDF."})

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y_position = height - 50
    for mcq in mcq_list:
        p.drawString(100, y_position, f"Question: {mcq['question']}")
        y_position -= 20
        for option in mcq['options']:
            p.drawString(120, y_position, f"- {option}")
            y_position -= 15
        y_position -= 30

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="mcqs.pdf")


# Utility Functions
def extract_keywords_based_on_option(option, context, num_keywords):
    """Extract keywords based on the selected option."""
    if option == 'spacy':
        from apps.keywordExtraction import get_keywords
        from apps.summarization import summarizer, summary_model, summary_tokenizer
        
        summary_text = summarizer(context, summary_model, summary_tokenizer)
        return get_keywords(context, summary_text, num_keywords)
    
    elif option == 'rake':
        from apps.rakeKeyword import get_keywords_rake
        return get_keywords_rake(context, num_keywords)
    
    elif option == 'distilBERT':
        from apps.distilBERTKeyword import extract_keywords
        return extract_keywords(context, num_keywords=num_keywords)
    
    return []


def generate_questions_and_distractors(option_1, option_3, context, keywords):
    """Generate questions and distractors for given keywords."""
    questions_dict = {}
    distractors_dict = {}

    # Lazy load models for question generation and distractor generation
    question_model, question_tokenizer = None, None
    dis_model, dis_tokenizer = None, None

    if option_1 == "general":
        from apps.questionGeneration import get_question, question_model, question_tokenizer
    elif option_1 == "t5-llm":
        from apps.question_gen_science import get_question_science, question_model, question_tokenizer

    if option_3 == "t5-llm":
        from apps.t5distractors import dis_model, dis_tokenizer, get_distractors_t5
    elif option_3 == "llama":
        from apps.llama_distractors import generate_distractors_llama
    elif option_3 == "s2v":
        from apps.s2vdistractors import generate_distractors, s2v

    for keyword in keywords:
        # Generate question
        if option_1 == "general":
            question = get_question(context, keyword, question_model, question_tokenizer)
        elif option_1 == "t5-llm":
            question = get_question_science(context, keyword, question_model, question_tokenizer)
        else:
            question = f"What is {keyword}?"  # Fallback question

        print(f"Option 1: {option_1}, Using T5 Model: {option_1 in ['general', 't5-llm']}")  # Debugging statement

        # Generate distractors
        if option_3 == "t5-llm":
            distractors = get_distractors_t5(
                question=question,
                answer=keyword,
                context=context,
                model=dis_model,
                tokenizer=dis_tokenizer
            )
        elif option_3 == "llama":
            distractors = generate_distractors_llama(context, question, keyword)
        elif option_3 == "s2v":
            distractors = generate_distractors(keyword, s2v)
        else:
            distractors = []

        questions_dict[keyword] = question
        distractors_dict[keyword] = distractors

    return questions_dict, distractors_dict



def create_mcq_list(keywords, questions_dict, distractors_dict):
    """Combine questions and distractors into MCQ format."""
    mcq_list = []
    for keyword in keywords:
        question = questions_dict[keyword]
        correct_answer = keyword
        distractors = distractors_dict[keyword]

        # Combine correct answer with distractors and shuffle them
        options = [correct_answer] + distractors
        random.shuffle(options)

        mcq_list.append(
            {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
            }
        )
    return mcq_list

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        
        if User.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already in use'})
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        login(request, user)
        return JsonResponse({'success': True, 'message': 'Registration successful'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        print(f'CSRF token: {request.COOKIES.get("csrftoken")}')

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
           
            return JsonResponse({'success': True, 'message': 'Login successful'})
           
        else:
           
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})
              
    return JsonResponse({'success': False, 'message': 'Invalid request'})
      
def is_logged_in(request):
    return JsonResponse({'logged_in': request.user.is_authenticated})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('generate_mcq')  # Redirect after logout
    return redirect('generate_mcq') 


def test(request):
    latest_batch = MCQ.objects.latest('created_at')
    mcq_list = json.loads(latest_batch.mcqs)
    mcq_list=ast.literal_eval(mcq_list)  #converts json string to list
    if request.method == 'POST':
        score = 0
        for i, mcq in enumerate(mcq_list):
            selected_option = request.POST.get(f'option_{i}')
            correct_answer = mcq["correct_answer"]
            if selected_option == correct_answer:
                score += 1
        return render(request, 'quesGens/test_results.html', {'score': score, 'total': len(mcq_list)})

    return render(request, 'quesGens/test.html', {'mc_list': mcq_list})



# @login_required
def history(request):
    if request.user.is_authenticated:
       mcq_entries = MCQ.objects.filter(user=request.user).order_by('-created_at')  # Fetch all MCQ entries for the logged-in user
    #    mcq_entries= ast.literal_eval(mcq_entries)
       print(type(mcq_entries))
    else:
       mcq_entries=request.session.get('mcqs',None) # mcq_entries is the list of single dictonary
    history_data = []
    if mcq_entries:
        if isinstance(mcq_entries, str):   # If mcq_entries is a string (session data), deserialize it
            mcq_entries = json.loads(mcq_entries)  # Convert JSON string back to Python object
            # mcq_entries= ast.literal_eval(mcq_entries)
            history_data.append({
                    "id": None,  
                    "mcqs": mcq_entries, 
                    "created_at": None, 
                })
        else:
            for entry in mcq_entries:  # entry refers to each obj in mcq_entries
                mcqs = json.loads(entry.mcqs)  # Convert JSON string back to Python data
                mcqs= ast.literal_eval(mcqs)
                history_data.append({
                    "id": entry.id,
                    "mcqs": mcqs, # mcqs is the attribute containing list of mcq 
                    "created_at": entry.created_at,
                })  # history_data is the list of list of dictionary of mcqs

    return render(request, "quesGens/history.html", {"history_data": history_data})




# @login_required
def delete_history(request, entry_id):
    if request.user.is_authenticated:
        mcq_entry = get_object_or_404(MCQ, id=entry_id, user=request.user) # Get the MCQ entry for the logged-in user
        mcq_entry.delete()
    else:
        del request.session['mcqs']  #delete the entries of random non-logged user from the session.
    return redirect('history')
def about(request):
    return render(request,'quesGens/about.html')


# @login_required
# def profile(request):
#     if request.method == 'POST':
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(request.POST,
#                                     request.FILES,
#                                     instance=request.user.profile)
#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             messages.success(request, f'Your account has been updated! You are able to login')
#             return redirect('profile')
#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profile)
#         context ={
#         'u_form':u_form,
#         'p_form':p_form
#          }
#     return render(request,'quesGens/profile.html',context)


# anuj
# 1234