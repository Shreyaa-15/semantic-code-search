import os
import json
import numpy as np
import faiss
from tqdm import tqdm
from db import get_all_snippets, init_db
from embedder import embed_texts, build_corpus_text

INDEX_PATH  = "data/code.index"
IDS_PATH    = "data/ids.json"

_index = None
_ids   = None


def build_index():
    """Embed all snippets and build FAISS index. Saves to disk."""
    print("Loading snippets from DB...")
    snippets = get_all_snippets()
    print(f"Found {len(snippets)} snippets")

    if not snippets:
        print("No snippets found — run the scraper first.")
        return

    # Build corpus texts
    texts = [build_corpus_text(s) for s in snippets]
    ids   = [s["id"] for s in snippets]

    # Generate embeddings
    print("Generating embeddings (this takes a few minutes)...")
    embeddings = embed_texts(texts)

    # Build FAISS index
    # IndexFlatIP = exact inner product search (cosine similarity after normalization)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Save index and id mapping
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(IDS_PATH, "w") as f:
        json.dump(ids, f)

    print(f"Index built: {index.ntotal} vectors, dim={dim}")
    print(f"Saved to {INDEX_PATH}")
    return index, ids


def load_index():
    """Load FAISS index from disk."""
    global _index, _ids
    if _index is not None:
        return _index, _ids

    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("Index not found — run build_index() first")

    _index = faiss.read_index(INDEX_PATH)
    with open(IDS_PATH) as f:
        _ids = json.load(f)

    print(f"Index loaded: {_index.ntotal} vectors")
    return _index, _ids


def search_index(query_embedding: np.ndarray, top_k: int = 20) -> list[tuple]:
    """
    Search FAISS index.
    Returns list of (snippet_id, score) tuples sorted by score descending.
    """
    index, ids = load_index()
    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        snippet_id = ids[idx]
        results.append((snippet_id, float(score)))

    return results


if __name__ == "__main__":
    init_db()
    build_index()