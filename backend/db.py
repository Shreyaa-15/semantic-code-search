import sqlite3
import json

DB_PATH = "data/code_search.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    import os
    os.makedirs("data", exist_ok=True)
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS snippets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            repo        TEXT NOT NULL,
            filepath    TEXT NOT NULL,
            language    TEXT NOT NULL,
            function_name TEXT NOT NULL,
            code        TEXT NOT NULL,
            docstring   TEXT DEFAULT '',
            stars       INTEGER DEFAULT 0,
            url         TEXT DEFAULT ''
        );
    """)
    conn.commit()
    conn.close()

def insert_snippet(repo, filepath, language, function_name, code, docstring, stars, url):
    conn = get_conn()
    conn.execute("""
        INSERT INTO snippets (repo, filepath, language, function_name, code, docstring, stars, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (repo, filepath, language, function_name, code, docstring, stars, url))
    conn.commit()
    conn.close()

def get_snippets_by_ids(ids: list[int]) -> list[dict]:
    conn = get_conn()
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT * FROM snippets WHERE id IN ({placeholders})", ids
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_snippets() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM snippets").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM snippets").fetchone()[0]
    langs = conn.execute(
        "SELECT language, COUNT(*) as count FROM snippets GROUP BY language"
    ).fetchall()
    repos = conn.execute(
        "SELECT COUNT(DISTINCT repo) FROM snippets"
    ).fetchone()[0]
    conn.close()
    return {
        "total_snippets": total,
        "total_repos": repos,
        "by_language": {r["language"]: r["count"] for r in langs}
    }

def clear_snippets():
    conn = get_conn()
    conn.execute("DELETE FROM snippets")
    conn.commit()
    conn.close()