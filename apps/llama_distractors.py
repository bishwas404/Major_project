from langchain_ollama import OllamaLLM

model = OllamaLLM(model="mymodel:latest")

def generate_distractors_llama(context: str, question: str, answer: str) -> list:
    messages = [
    {
        "role": "system",
        "content": """You are an expert at generating plausible but incorrect options for multiple-choice questions.
    Your distractors must:
    - Be grammatically consistent with the question
    - Be similar in length to the correct answer
    - Be related to the topic but clearly incorrect
    - Not be obviously wrong or humorous
    - Be unique from each other
    - Be more than or equal to four.
    - not contain any word similar to actual correct answer
    - Follow a similar structure each time"""
        },
        {
            "role": "user",
            "content": f"""Given the following:
    Context: {context}
    Question: {question}
    Correct Answer: {answer}

    Generate exactly three distractors that are:
    1. Plausible alternatives to the correct answer
    2. Related to the context
    3. Similar in format to the correct answer

    Provide only the three distractors as a comma-separated list without any additional text."""
        }
    ]
    
    response = model.invoke(messages)
    return [opt.strip() for opt in response.split(',') if opt.strip()][:3]

if __name__ == "__main__":
    context ="""The human heart is an organ that pumps blood through the body via the circulatory system."""
    question = "What is the human heart?"
    answer = "An organ that pumps blood"
    print(generate_distractors_llama(context=context, question=question, answer=answer))
