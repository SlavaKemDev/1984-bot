import fasttext
from huggingface_hub import hf_hub_download
import numpy as np
from typing import List, Union

class FastTextEmbedder:
    _model = None

    def __init__(self, model_name: str = "facebook/fasttext-ru-vectors"):
        if FastTextEmbedder._model is None:
            model_path = hf_hub_download(repo_id=model_name, filename="model.bin")
            FastTextEmbedder._model = fasttext.load_model(model_path)

    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            return self.get_embeddings([texts])[0]

        return np.array([FastTextEmbedder._model.get_sentence_vector(text) for text in texts])
