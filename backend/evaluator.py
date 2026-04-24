"""
Evaluation module — computes MRR and NDCG.
Compares semantic search vs BM25 baseline.

Test set format:
  [{"query": "binary search", "relevant_function": "binary_search"}, ...]

MRR  = mean reciprocal rank (how high is the first correct result?)
NDCG = normalized discounted cumulative gain (quality of full ranking)
"""

import math
from search import semantic_search, bm25_only_search

TEST_SET = [
    {"query": "binary search in sorted array",        "relevant_function": "binary_search"},
    {"query": "merge two sorted lists",               "relevant_function": "merge_sort"},
    {"query": "check if string is palindrome",        "relevant_function": "is_palindrome"},
    {"query": "find factorial of a number",           "relevant_function": "factorial"},
    {"query": "reverse a linked list",                "relevant_function": "reverse"},
    {"query": "bubble sort algorithm",                "relevant_function": "bubble_sort"},
    {"query": "find fibonacci sequence",              "relevant_function": "fibonacci"},
    {"query": "depth first search graph traversal",   "relevant_function": "dfs"},
    {"query": "check if number is prime",             "relevant_function": "is_prime"},
    {"query": "calculate greatest common divisor",    "relevant_function": "gcd"},
    {"query": "stack push and pop operations",        "relevant_function": "push"},
    {"query": "hash map get and set",                 "relevant_function": "get"},
    {"query": "quicksort partition array",            "relevant_function": "quick_sort"},
    {"query": "breadth first search",                 "relevant_function": "bfs"},
    {"query": "find maximum subarray sum",            "relevant_function": "max_subarray"},
]


def reciprocal_rank(results: list[dict], relevant_function: str) -> float:
    """Return 1/rank of first relevant result, or 0 if not found."""
    for i, r in enumerate(results):
        if relevant_function.lower() in r["function_name"].lower():
            return 1.0 / (i + 1)
    return 0.0


def dcg(results: list[dict], relevant_function: str, k: int = 10) -> float:
    """Discounted Cumulative Gain at k."""
    score = 0.0
    for i, r in enumerate(results[:k]):
        if relevant_function.lower() in r["function_name"].lower():
            score += 1.0 / math.log2(i + 2)
    return score


def ndcg(results: list[dict], relevant_function: str, k: int = 10) -> float:
    """Normalized DCG — divides by ideal DCG (perfect ranking)."""
    ideal = 1.0 / math.log2(2)  # best case: relevant result at rank 1
    actual = dcg(results, relevant_function, k)
    return actual / ideal if ideal > 0 else 0.0


def evaluate(top_k: int = 10) -> dict:
    """
    Run full evaluation on test set.
    Compares semantic search vs BM25 baseline.
    Returns MRR and NDCG for both methods.
    """
    semantic_rr   = []
    semantic_ndcg = []
    bm25_rr       = []
    bm25_ndcg     = []

    print(f"\nEvaluating on {len(TEST_SET)} queries...\n")
    print(f"{'Query':<45} {'Sem RR':>8} {'BM25 RR':>8}")
    print("-" * 65)

    for item in TEST_SET:
        query    = item["query"]
        relevant = item["relevant_function"]

        # Semantic search
        sem_results  = semantic_search(query, top_k=top_k, rerank=True)
        sem_rr_val   = reciprocal_rank(sem_results, relevant)
        sem_ndcg_val = ndcg(sem_results, relevant, k=top_k)

        # BM25 baseline
        bm25_results  = bm25_only_search(query, top_k=top_k)
        bm25_rr_val   = reciprocal_rank(bm25_results, relevant)
        bm25_ndcg_val = ndcg(bm25_results, relevant, k=top_k)

        semantic_rr.append(sem_rr_val)
        semantic_ndcg.append(sem_ndcg_val)
        bm25_rr.append(bm25_rr_val)
        bm25_ndcg.append(bm25_ndcg_val)

        print(f"{query:<45} {sem_rr_val:>8.3f} {bm25_rr_val:>8.3f}")

    mrr_semantic = sum(semantic_rr)   / len(semantic_rr)
    mrr_bm25     = sum(bm25_rr)       / len(bm25_rr)
    ndcg_semantic = sum(semantic_ndcg) / len(semantic_ndcg)
    ndcg_bm25    = sum(bm25_ndcg)     / len(bm25_ndcg)

    print("-" * 65)
    print(f"\nResults:")
    print(f"  Semantic MRR:  {mrr_semantic:.4f}")
    print(f"  BM25 MRR:      {mrr_bm25:.4f}")
    print(f"  Semantic NDCG: {ndcg_semantic:.4f}")
    print(f"  BM25 NDCG:     {ndcg_bm25:.4f}")
    print(f"\n  Semantic vs BM25 MRR improvement: {((mrr_semantic - mrr_bm25) / max(mrr_bm25, 0.001)) * 100:.1f}%")

    return {
        "semantic": {"mrr": round(mrr_semantic, 4), "ndcg": round(ndcg_semantic, 4)},
        "bm25":     {"mrr": round(mrr_bm25, 4),     "ndcg": round(ndcg_bm25, 4)},
        "improvement_pct": round(((mrr_semantic - mrr_bm25) / max(mrr_bm25, 0.001)) * 100, 1)
    }


if __name__ == "__main__":
    evaluate()