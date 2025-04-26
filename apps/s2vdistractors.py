import os

import nltk
from nltk.corpus import wordnet as wn
from sense2vec import Sense2Vec

# Configure NLTK to use a custom data directory
NLTK_DATA_DIR = 'D:\\Files\\question_answering\\.venv\\Lib\\nltk_data'
nltk.data.path.append(NLTK_DATA_DIR)

# Check for WordNet and download if not present
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', download_dir=NLTK_DATA_DIR)

# Load Sense2Vec model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
S2V_MODEL_PATH = os.path.join(BASE_DIR, "s2v_old")
s2v = Sense2Vec().from_disk(S2V_MODEL_PATH)

# Function to generate distractors using Sense2Vec
def get_distractors_s2v(answer, s2v_model):
    distractors = set()
    word = answer.lower().replace(" ", "_")
    try:
        sense = s2v_model.get_best_sense(word)
        if sense:
            most_similar = s2v_model.most_similar(sense, n=5)
            for similar_word, _ in most_similar:
                clean_word = similar_word.split("|")[0].replace("_", " ")
                if clean_word.lower() != answer.lower():
                    distractors.add(clean_word)
    except KeyError:
        pass
    return list(distractors)[:3]

# Function to generate distractors using WordNet
def get_distractors_wordnet(answer):
    distractors = set()
    for syn in wn.synsets(answer):
        for lemma in syn.lemmas():
            word = lemma.name().replace("_", " ")
            if word.lower() != answer.lower():
                distractors.add(word)
            if len(distractors) >= 3:
                break
        if len(distractors) >= 3:
            break
    return list(distractors)[:3]

# Combined function to generate distractors
def generate_distractors(answer, s2v_model):
    # First, try Sense2Vec
    distractors = get_distractors_s2v(answer, s2v_model)
    
    # If fewer than 3 distractors are found, use WordNet to supplement
    if len(distractors) < 3:
        additional_distractors = get_distractors_wordnet(answer)
        combined_distractors = distractors + [d for d in additional_distractors if d not in distractors]
        distractors = combined_distractors[:3]
    
    # Ensure we have 3 distractors
    if len(distractors) < 3:
        print("Warning: Could not find 3 distinct distractors.")
    
    return distractors

# Example usage
if __name__ == "__main__":
    answer = "bitcoin"
    distractors = generate_distractors(answer, s2v)
    print("Generated Distractors:", distractors)
