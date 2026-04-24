import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from db import init_db, get_stats
from search import semantic_search, bm25_only_search
from indexer import build_index, load_index
from evaluator import evaluate

load_dotenv()

app = FastAPI(title="Semantic Code Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    try:
        load_index()
        print("FAISS index loaded.")
    except FileNotFoundError:
        print("No index found — run POST /index to build it.")

# --- Models ---

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    language: str = "all"
    rerank: bool = True

class IndexRequest(BaseModel):
    repos: list[str] = []

# --- Endpoints ---

@app.post("/search")
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = semantic_search(
        query=req.query,
        top_k=req.top_k,
        language=req.language if req.language != "all" else None,
        rerank=req.rerank
    )
    return {
        "query": req.query,
        "total": len(results),
        "results": results
    }

@app.post("/search/bm25")
def search_bm25(req: SearchRequest):
    results = bm25_only_search(
        query=req.query,
        top_k=req.top_k,
        language=req.language if req.language != "all" else None
    )
    return {"query": req.query, "total": len(results), "results": results}

@app.get("/stats")
def stats():
    return get_stats()

@app.post("/index")
def trigger_index():
    """Rebuild the FAISS index from current DB contents."""
    try:
        build_index()
        return {"status": "ok", "message": "Index built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate")
def run_evaluation():
    """Run MRR + NDCG evaluation and return results."""
    try:
        results = evaluate()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}