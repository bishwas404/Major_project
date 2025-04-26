import re
import unicodedata

def clean_text(text: str) -> str:
    """Clean the text by removing extra symbols and spaces.

    Args:
        text (str): The input text.

    Returns:
        str: Cleaned text.
    """
    text = _remove_brackets(text)
    text = _remove_square_brackets(text)
    text = _replace_unicode_hyphen(text)
    text = _remove_multiple_spaces(text)
    return text.strip()


def _remove_brackets(text: str) -> str:
    """Remove parentheses and content inside them."""
    return re.sub(r'\([^)]*\)', '', text)


def _remove_square_brackets(text: str) -> str:
    """Remove square brackets and content inside them."""
    return re.sub(r'\[[^\]]*\]', '', text)


def _remove_multiple_spaces(text: str) -> str:
    """Replace multiple spaces with a single space."""
    return re.sub(r'\s+', ' ', text)


def _replace_unicode_hyphen(text: str) -> str:
    """Normalize hyphens to standard ASCII hyphen ('-')."""
    return unicodedata.normalize("NFKC", text).replace('–', '-')