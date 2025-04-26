import os

import numpy as np
from peft import PeftConfig, PeftModel
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers.pipelines import AggregationStrategy, TokenClassificationPipeline

base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of `t5distractors.py`
base_tokenizer_path = os.path.join(base_dir, "base-distilBERT", "tokenizer")
base_model_path = os.path.join(base_dir,"base-distilBERT", "model")
adapter_model_path = os.path.join(base_dir,"base-distilBERT", "adapter_model")

# Load PEFT configuration and base model
peft_config = PeftConfig.from_pretrained(adapter_model_path)
base_model = AutoModelForTokenClassification.from_pretrained(base_model_path)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_tokenizer_path)
tokenizer.pad_token = tokenizer.eos_token

# Load the fine-tuned adapter model and merge with the base model
peft_model = PeftModel.from_pretrained(base_model, adapter_model_path)
merged_model = peft_model.merge_and_unload()

# Custom pipeline for keyphrase extraction
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, tokenizer, max_keywords=None, *args, **kwargs):
        super().__init__(model=model, tokenizer=tokenizer, *args, **kwargs)
        self.max_keywords = max_keywords

    def postprocess(self, model_outputs):
        # Process model outputs to extract unique keywords
        results = super().postprocess(model_outputs, aggregation_strategy=AggregationStrategy.FIRST)
        keywords = np.unique([result.get("word").strip() for result in results])

        # Sort by score if available
        if results and "score" in results[0]:
            keyword_scores = {result["word"].strip(): result["score"] for result in results}
            sorted_keywords = sorted(keyword_scores, key=keyword_scores.get, reverse=True)
        else:
            sorted_keywords = keywords

        # Limit keywords if max_keywords is specified
        if self.max_keywords is not None:
            sorted_keywords = sorted_keywords[:self.max_keywords]

        return sorted_keywords

# Function to extract keywords
def extract_keywords(text, num_keywords=None, device='cpu'):
    extractor = KeyphraseExtractionPipeline(
        model=merged_model,
        tokenizer=tokenizer,
        max_keywords=num_keywords,
        device=device
    )
    keyphrases = extractor(text)
    return keyphrases

if __name__ == "__main__":
    # Example text for extraction
    text = """
    In a village, lived a carefree boy with his father. The boy’s father told him that he was old enough to watch over the sheep while they graze in the fields. Every day, he had to take the sheep to the grassy fields and watch them as they graze. However, the boy was unhappy and didn’t want to take the sheep to the fields. He wanted to run and play, not watch the boring sheep graze in the field. So, he decided to have some fun. He cried, “Wolf! Wolf!” until the entire village came running with stones to chase away the wolf before it could eat any of the sheep. When the villagers saw that there was no wolf, they left muttering under their breath about how the boy had wasted their time. The next day, the boy cried once more, “Wolf! Wolf!” and, again, the villagers rushed there to chase the wolf away.

    The boy laughed at the fright he had caused. This time, the villagers left angrily. The third day, as the boy went up the small hill, he suddenly saw a wolf attacking his sheep. He cried as hard as he could, “Wolf! Wolf! Wolf!”, but not a single villager came to help him. The villagers thought that he was trying to fool them again and did not come to rescue him or his sheep. The little boy lost many sheep that day, all because of his foolishness.
    """
    
    # Extract keywords
    keywords = extract_keywords(text, num_keywords=5)
    print("Keywords:", keywords)
    print(type(keywords))