import nltk
from rake_nltk import Rake

# Set custom NLTK data path
nltk.data.path.append('D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Ensure required nltk resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')


try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')


def get_keywords_rake(content, num_keywords=4):
    """
    Extract keywords from the content using the RAKE algorithm.
    Returns sorted keywords without scores, prioritizing nouns and pronouns.
    """
    # Initialize Rake with specific parameters for consistency
    r = Rake(min_length=1, max_length=4)
    r.extract_keywords_from_text(content)
    
    # Get ranked phrases
    keywords = list(set(r.get_ranked_phrases()))
    
    # Filter to retain phrases with nouns or pronouns
    filtered_keywords = []
    for phrase in keywords:
        words = nltk.word_tokenize(phrase)
        pos_tags = nltk.pos_tag(words)
        
        # Keep the phrase if it has nouns (NN, NNS, NNP, NNPS) or pronouns (PRP, PRP$)
        if any(tag.startswith('NN') or tag.startswith('PRP') for word, tag in pos_tags):
            filtered_keywords.append(phrase)
    
    # Sort alphabetically for consistency
    filtered_keywords.sort()
    
    # Return top keywords based on num_keywords
    return filtered_keywords[:num_keywords]


# Sample text
texts = """The Solar System consists of the Sun and the celestial bodies that orbit it, 
    including eight planets, their moons, and various dwarf planets, asteroids, and comets. 
    The four inner planets—Mercury, Venus, Earth, and Mars—are rocky, whereas the outer planets—Jupiter, 
    Saturn, Uranus, and Neptune—are gas giants. The asteroid belt, located between Mars and Jupiter, 
    contains numerous rocky objects. Beyond Neptune lies the Kuiper Belt, home to icy bodies such as Pluto. 
    The Sun, a massive ball of plasma, provides the energy that sustains life on Earth. Gravity keeps the planets in orbit, 
    and their interactions with the Sun influence climate and weather patterns. Scientists continue to explore the 
    mysteries of our Solar System using telescopes and space probes, expanding our knowledge of the universe.
    """

if __name__ == "__main__":
    # Extract keywords using RAKE
    keywords = get_keywords_rake(texts, num_keywords=10)
    print("Keywords:", keywords)
    print(type(keywords))