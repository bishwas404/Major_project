import re
import os
import spacy
from collections import Counter
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import PreTrainedTokenizerFast

# Load spaCy for sentence tokenization and keyword extraction
# Check if spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Downloading...")
    # Download spaCy model if not found
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """Extracts top N keywords using a simple frequency-based approach."""
    doc = nlp(text)
    words = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    common_keywords = [word for word, _ in Counter(words).most_common(num_keywords)]
    return common_keywords

def rank_sentences(text: str, keywords: List[str]) -> List[str]:
    """Ranks sentences based on keyword density."""
    sentences = sent_tokenize(text)
    sentence_scores = {sent: sum(1 for word in word_tokenize(sent.lower()) if word in keywords) for sent in sentences}
    ranked_sentences = sorted(sentences, key=lambda s: sentence_scores[s], reverse=True)
    return ranked_sentences

def keyword_centric_chunking(text: str, tokenizer: PreTrainedTokenizerFast, max_tokens: int = 512) -> List[str]:
    """Splits the text into chunks based on keyword relevance while maintaining token limits."""
    keywords = extract_keywords(text)
    ranked_sentences = rank_sentences(text, keywords)
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for sentence in ranked_sentences:
        token_count = len(tokenizer.tokenize(sentence))
        if current_token_count + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_token_count = 0
        
        current_chunk.append(sentence)
        current_token_count += token_count
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks