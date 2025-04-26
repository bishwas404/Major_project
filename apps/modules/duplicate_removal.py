from typing import List
import string
import re
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def remove_duplicates(items: List[str]) -> List[str]:
    """Remove duplicate items based on normalized values."""
    seen = set()
    unique_items = []

    for item in items:
        normalized_item = _normalize_item(item)
        if normalized_item not in seen:
            seen.add(normalized_item)
            unique_items.append(item)

    return unique_items


def remove_distractors_duplicate_with_correct_answer(correct: str, distractors: List[str]) -> List[str]:
    """Remove distractors that are identical to the correct answer."""
    normalized_correct = _normalize_item(correct)
    return [distractor for distractor in distractors if _normalize_item(distractor) != normalized_correct]


def _normalize_item(item: str) -> str:
    """Normalize text by lowering case, removing punctuation, articles, and extra spaces."""
    item = item.lower()
    item = re.sub(r'\b(a|an|the)\b', ' ', item)  # Remove articles
    item = ''.join(ch for ch in item if ch not in string.punctuation)  # Remove punctuation
    return ' '.join(item.split())  # Remove extra spaces


def _calculate_nltk_bleu(references: List[str], hypothesis: str, bleu_n: int = 1) -> float:
    """Calculate BLEU score for a hypothesis against reference texts."""
    if not hypothesis:
        return 0.0

    refs_tokenized = [word_tokenize(ref) for ref in references]
    hyp_tokenized = word_tokenize(hypothesis)

    chencherry = SmoothingFunction()
    weights_dict = {
        1: (1, 0, 0, 0),
        2: (0.5, 0.5, 0, 0),
        3: (0.33, 0.33, 0.33, 0),
        4: (0.25, 0.25, 0.25, 0.25),
    }
    
    return sentence_bleu(refs_tokenized, hyp_tokenized, weights=weights_dict.get(bleu_n, (1, 0, 0, 0)), smoothing_function=chencherry.method2)


def _get_most_distinct_from_each_other(items: List[str], max_items: int) -> List[str]:
    """Select the most distinct items based on BLEU scores."""
    if len(items) <= max_items:
        return items

    distinct_items = [items[0]]
    
    while len(distinct_items) < max_items and len(items) > 1:
        items.sort(key=lambda x: min(_calculate_nltk_bleu([d], x) for d in distinct_items))
        distinct_items.append(items.pop(0))

    return distinct_items