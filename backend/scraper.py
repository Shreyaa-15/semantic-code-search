import os
import ast
import time
import re
from github import Github
from dotenv import load_dotenv
from tqdm import tqdm
from db import init_db, insert_snippet, get_stats

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

# Popular repos to scrape — mix of algorithms, utilities, ML, web
REPOS_TO_SCRAPE = [
    "TheAlgorithms/Python",
    "TheAlgorithms/JavaScript",
    "keon/algorithms",
    "donnemartin/system-design-primer",
    "pallets/flask",
    "psf/requests",
    "scikit-learn/scikit-learn",
    "numpy/numpy",
]

MAX_FUNCTIONS_PER_REPO = 200
MAX_FILE_SIZE_KB = 50


def extract_python_functions(source: str, filepath: str, repo_name: str, stars: int, url: str):
    """Parse Python source and extract all function definitions with docstrings."""
    snippets = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return snippets

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private/dunder functions
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            if node.name.startswith("_"):
                continue

            # Get source lines for this function
            try:
                lines = source.splitlines()
                start = node.lineno - 1
                end = node.end_lineno
                func_source = "\n".join(lines[start:end])
            except Exception:
                continue

            # Skip very short or very long functions
            if len(func_source) < 50 or len(func_source) > 2000:
                continue

            # Extract docstring
            docstring = ast.get_docstring(node) or ""

            snippets.append({
                "repo": repo_name,
                "filepath": filepath,
                "language": "python",
                "function_name": node.name,
                "code": func_source,
                "docstring": docstring,
                "stars": stars,
                "url": url
            })

    return snippets


def extract_js_functions(source: str, filepath: str, repo_name: str, stars: int, url: str):
    """Extract JavaScript functions using regex — no full JS parser needed."""
    snippets = []

    # Match: function name(...) { ... } and arrow functions assigned to const/let
    patterns = [
        r'(?:^|\n)(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{',
        r'(?:^|\n)(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{',
    ]

    lines = source.splitlines()

    for pattern in patterns:
        for match in re.finditer(pattern, source, re.MULTILINE):
            func_name = match.group(1)
            if func_name.startswith("_"):
                continue

            start_pos = match.start()
            start_line = source[:start_pos].count("\n")

            # Find the closing brace by counting braces
            brace_count = 0
            end_line = start_line
            in_func = False

            for i, line in enumerate(lines[start_line:], start=start_line):
                brace_count += line.count("{") - line.count("}")
                if brace_count > 0:
                    in_func = True
                if in_func and brace_count <= 0:
                    end_line = i
                    break

            func_source = "\n".join(lines[start_line:end_line + 1])

            if len(func_source) < 50 or len(func_source) > 2000:
                continue

            # Try to extract JSDoc comment above the function
            docstring = ""
            if start_line > 0:
                prev_lines = lines[max(0, start_line-10):start_line]
                jsdoc = []
                in_jsdoc = False
                for l in reversed(prev_lines):
                    stripped = l.strip()
                    if stripped.endswith("*/"):
                        in_jsdoc = True
                    if in_jsdoc:
                        jsdoc.insert(0, stripped)
                    if stripped.startswith("/**"):
                        break
                docstring = " ".join(jsdoc)

            snippets.append({
                "repo": repo_name,
                "filepath": filepath,
                "language": "javascript",
                "function_name": func_name,
                "code": func_source,
                "docstring": docstring,
                "stars": stars,
                "url": url
            })

    return snippets


def scrape_repo(repo_name: str, max_functions: int = MAX_FUNCTIONS_PER_REPO) -> int:
    """Scrape a single GitHub repo and store functions in SQLite."""
    print(f"\nScraping {repo_name}...")
    count = 0

    try:
        repo = g.get_repo(repo_name)
        stars = repo.stargazers_count

        # Get all Python and JS files
        contents = repo.get_git_tree(sha="HEAD", recursive=True).tree
        files = [
            f for f in contents
            if f.path.endswith((".py", ".js"))
            and f.size
            and f.size < MAX_FILE_SIZE_KB * 1024
        ]

        for file in tqdm(files, desc=f"  Files in {repo_name.split('/')[1]}"):
            if count >= max_functions:
                break
            try:
                content = repo.get_contents(file.path)
                source = content.decoded_content.decode("utf-8", errors="ignore")
                file_url = f"https://github.com/{repo_name}/blob/HEAD/{file.path}"

                if file.path.endswith(".py"):
                    snippets = extract_python_functions(source, file.path, repo_name, stars, file_url)
                else:
                    snippets = extract_js_functions(source, file.path, repo_name, stars, file_url)

                for s in snippets:
                    if count >= max_functions:
                        break
                    insert_snippet(**s)
                    count += 1

                time.sleep(0.1)  # be polite to GitHub API

            except Exception as e:
                continue

    except Exception as e:
        print(f"  Error scraping {repo_name}: {e}")

    print(f"  Extracted {count} functions from {repo_name}")
    return count


def run_scraper(repos=None):
    """Run the full scraping pipeline."""
    init_db()
    repos = repos or REPOS_TO_SCRAPE
    total = 0

    for repo_name in repos:
        total += scrape_repo(repo_name)
        time.sleep(1)  # pause between repos

    print(f"\nDone. Total functions scraped: {total}")
    stats = get_stats()
    print(f"Stats: {stats}")
    return stats


if __name__ == "__main__":
    run_scraper()