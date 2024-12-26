import numpy as np
from typing import List, Union
import compress_fasttext


class FastTextEmbedder:
    _model = None

    def __init__(self, model_path: str = "models/fasttext.vec"):
        if FastTextEmbedder._model is None:
            FastTextEmbedder._model = compress_fasttext.models.CompressedFastTextKeyedVectors.load(model_path)

    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            return self.get_embeddings([texts])[0]

        return np.array([FastTextEmbedder._model.get_sentence_vector(text) for text in texts])

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
