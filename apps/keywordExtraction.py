import os

import nltk
import pke
import spacy
from flashtext import KeywordProcessor
from nltk.corpus import stopwords

# Set custom NLTK data path
nltk.data.path.append('D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Ensure required nltk resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Check if spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Downloading...")
    # Download spaCy model if not found
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")



def get_nouns_multipartite(content):
    """
    Extract top-ranked noun phrases from the content using the MultipartiteRank algorithm.
    """
    try:
        # Initialize the extractor
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=content, language="en", spacy_model=nlp)

        # Candidate selection: Include only proper nouns and nouns
        extractor.candidate_selection(pos={"PROPN", "NOUN"})

        # Weight candidates using MultipartiteRank
        extractor.candidate_weighting(alpha=1.1, threshold=0.75, method="average")

        # Extract top 15 keyphrases
        return [phrase for phrase, _ in extractor.get_n_best(n=15)]
    except Exception as e:
        print(f"Error in MultipartiteRank extraction: {e}")
        return []


def get_keywords(original_text, summary_text, num_keywords=4):
    """
    Extract and match keywords between original text and summary text.
    """
    # Extract keywords using MultipartiteRank
    keywords = get_nouns_multipartite(original_text)
    print("Keywords (unsummarized):", keywords)

    # Initialize KeywordProcessor
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list(keywords)

    # Extract matched keywords in the summary text
    keywords_found = set(keyword_processor.extract_keywords(summary_text))
    print("Keywords found in summary:", keywords_found)

    # Filter keywords to include only those appearing in both original and summary
    important_keywords = [keyword for keyword in keywords if keyword in keywords_found]

    # Return the top `num_keywords` important keywords
    return important_keywords[:num_keywords]


if __name__ == "__main__":
    # Sample text
    original_text = """There were two brothers; the older one was always mean to the younger one. 
    The older one would chop firewood in the forest and sell it in the market. One day, 
    he stumbled across a magical tree. The tree begged him not to cut him down and promised him golden apples in exchange. 
    The older brother felt disappointed with the number of apples he received. He decided to cut down the tree anyway,
    but the tree showered him with hundreds of needles"""
    summary_text = "Two brothers, older mean to younger. Older chops firewood, finds magical tree with golden apples. Disappointed, cuts tree, gets needles."

    # Extract keywords
    keywords = get_keywords(original_text, summary_text, num_keywords=5)
    print("Keywords:", keywords)
    print(type(keywords))
