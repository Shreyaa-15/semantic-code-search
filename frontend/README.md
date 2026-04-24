# Semantic Code Search Engine

Search real GitHub code using natural language instead of keywords.

**Example:** "find the maximum element in a list" → returns relevant functions even without keyword matches

## Features
- Natural language search over 1,683 real functions from 8 GitHub repos
- CodeBERT embeddings + FAISS vector similarity search
- BM25 re-ranking (70% semantic + 30% keyword hybrid)
- Evaluation with MRR and NDCG metrics vs BM25 baseline
- Syntax-highlighted results with repo links and star counts
- Language filter (Python / JavaScript)

## Tech Stack
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector search:** FAISS (IndexFlatIP — cosine similarity)
- **Re-ranking:** BM25 (rank-bm25)
- **Backend:** FastAPI
- **Frontend:** React + Vite
- **Storage:** SQLite + FAISS index on disk
- **Scraper:** PyGitHub + Python AST parser

## Architecture
1. **Scraper** — pulls Python/JS files from GitHub, extracts functions + docstrings
2. **Embedder** — converts each function to a 384-dim vector
3. **Indexer** — builds FAISS index for fast approximate nearest-neighbor search
4. **Search** — embeds query → FAISS top-50 → BM25 re-rank → top-10 results
5. **Evaluator** — measures MRR and NDCG on 15 test queries vs BM25 baseline

## Run Locally

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Scrape GitHub repos (needs GITHUB_TOKEN in .env)
python3 scraper.py

# Build FAISS index
python3 -c "from indexer import build_index; build_index()"

# Start API
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment Variables
Create `backend/.env`: