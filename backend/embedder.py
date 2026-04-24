import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32

_model = None

def load_model():
    global _model
    if _model is not None:
        return
    print("Loading embedding model...")
    _model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.")

def embed_texts(texts: list[str]) -> np.ndarray:
    load_model()
    embeddings = _model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    return embeddings.astype("float32")

def embed_query(query: str) -> np.ndarray:
    load_model()
    embedding = _model.encode(
        [query],
        normalize_embeddings=True
    )
    return embedding.astype("float32")

def build_corpus_text(snippet: dict) -> str:
    parts = []
    if snippet["function_name"]:
        name = snippet["function_name"].replace("_", " ")
        parts.append(name)
    if snippet["docstring"]:
        parts.append(snippet["docstring"])
    parts.append(snippet["code"])
    return " ".join(parts)[:512]