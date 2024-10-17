from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from typing import List, Union


class BertEmbedder:
    _tokenizer = None
    _model = None

    def __init__(self, model_name: str = 'DeepPavlov/rubert-base-cased'):
        # Initialize the BERT embedder with a specified model.

        if BertEmbedder._tokenizer is None or BertEmbedder._model is None:
            BertEmbedder._tokenizer = BertTokenizer.from_pretrained(model_name)
            BertEmbedder._model = BertModel.from_pretrained(model_name)

    def get_embeddings(self, texts: Union[str, List[str]]) -> torch.Tensor:
        # Get embeddings for a single text or a list of texts.

        if isinstance(texts, str):
            return self.get_embeddings([texts])[0]

        with torch.no_grad():
            inputs = BertEmbedder._tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
            outputs = BertEmbedder._model(**inputs)
            last_hidden_states = outputs.last_hidden_state

            # Mean pooling to obtain a single vector for each input
            return last_hidden_states.mean(dim=1).numpy()

    @staticmethod
    def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
