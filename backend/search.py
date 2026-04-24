from rank_bm25 import BM25Okapi
from db import get_snippets_by_ids, get_all_snippets
from embedder import embed_query, build_corpus_text
from indexer import search_index


def tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer for BM25."""
    return text.lower().split()


def semantic_search(
    query: str,
    top_k: int = 10,
    language: str = None,
    rerank: bool = True
) -> list[dict]:
    """
    Full search pipeline:
    1. Embed query with CodeBERT
    2. FAISS vector search → top 20 candidates
    3. BM25 re-ranking on top 20
    4. Filter by language if specified
    5. Return top_k results
    """

    # Step 1 — embed query
    query_embedding = embed_query(query)

    # Step 2 — FAISS search (get more candidates for re-ranking)
    candidates = search_index(query_embedding, top_k=50)

    if not candidates:
        return []

    # Step 3 — fetch snippet data
    candidate_ids = [c[0] for c in candidates]
    id_to_score   = {c[0]: c[1] for c in candidates}
    snippets = get_snippets_by_ids(candidate_ids)

    # Filter by language
    if language and language != "all":
        snippets = [s for s in snippets if s["language"] == language]

    if not snippets:
        return []

    # Step 4 — BM25 re-ranking
    if rerank and len(snippets) > 1:
        corpus = [tokenize(build_corpus_text(s)) for s in snippets]
        bm25   = BM25Okapi(corpus)
        bm25_scores = bm25.get_scores(tokenize(query))

        # Combine: 70% semantic + 30% BM25 (normalize BM25 to [0,1])
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        for i, snippet in enumerate(snippets):
            semantic_score = id_to_score.get(snippet["id"], 0)
            bm25_norm      = bm25_scores[i] / max_bm25
            snippet["score"]          = round(0.7 * semantic_score + 0.3 * bm25_norm, 4)
            snippet["semantic_score"] = round(float(semantic_score), 4)
            snippet["bm25_score"]     = round(float(bm25_norm), 4)

        snippets.sort(key=lambda x: x["score"], reverse=True)
    else:
        for snippet in snippets:
            snippet["score"] = round(id_to_score.get(snippet["id"], 0), 4)

    return snippets[:top_k]


def bm25_only_search(query: str, top_k: int = 10, language: str = None) -> list[dict]:
    """
    Pure BM25 keyword search — used as baseline for evaluation.
    """
    all_snippets = get_all_snippets()

    if language and language != "all":
        all_snippets = [s for s in all_snippets if s["language"] == language]

    if not all_snippets:
        return []

    corpus = [tokenize(build_corpus_text(s)) for s in all_snippets]
    bm25   = BM25Okapi(corpus)
    scores = bm25.get_scores(tokenize(query))

    for i, snippet in enumerate(all_snippets):
        snippet["score"] = round(float(scores[i]), 4)

    ranked = sorted(all_snippets, key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]