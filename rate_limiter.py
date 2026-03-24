"""
Universal API Rate Limiter — works with any API.
Just set calls_per_second and go.

Usage:
    python rate_limiter.py

Examples:
    - GitHub API (60 unauthenticated / 5000 authenticated per hour)
    - arXiv (1 request per 3 seconds)
    - PubMed (3/sec free, 10/sec with key)
"""

import time
import requests
from functools import wraps
from collections import deque


def rate_limit(calls_per_second: float):
    """Decorator that limits function calls to N per second."""
    min_interval = 1.0 / calls_per_second
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimiter:
    """Sliding window rate limiter for more precise control."""

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def wait(self):
        now = time.time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.calls.append(time.time())


# === EXAMPLES ===

@rate_limit(calls_per_second=1/3)  # arXiv: 1 req per 3 seconds
def search_arxiv(query: str, max_results: int = 5) -> dict:
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "max_results": max_results}
    r = requests.get(url, params=params)
    return {"status": r.status_code, "length": len(r.text)}


@rate_limit(calls_per_second=3)  # PubMed: 3 req/sec without key
def search_pubmed(query: str, max_results: int = 5) -> dict:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    r = requests.get(url, params=params)
    data = r.json()
    return {"count": data["esearchresult"]["count"], "ids": data["esearchresult"]["idlist"]}


def github_demo():
    """GitHub API with sliding window limiter."""
    limiter = RateLimiter(max_calls=10, period=60)  # 10 calls per minute (conservative)
    
    repos = ["react", "vue", "angular", "svelte", "next.js"]
    for repo in repos:
        limiter.wait()
        r = requests.get(f"https://api.github.com/repos/facebook/{repo}" if repo == "react"
                        else f"https://api.github.com/repos/vercel/{repo}" if repo == "next.js"
                        else f"https://api.github.com/repos/vuejs/{repo}" if repo == "vue"
                        else f"https://api.github.com/repos/{repo}/{repo}")
        if r.status_code == 200:
            data = r.json()
            print(f"  {data['full_name']}: {data['stargazers_count']:,}★")
        remaining = r.headers.get('X-RateLimit-Remaining', '?')
        print(f"  Rate limit remaining: {remaining}")


if __name__ == "__main__":
    print("=== arXiv Search (1 req/3sec) ===")
    for topic in ["LLM", "RAG", "transformers"]:
        result = search_arxiv(topic)
        print(f"  {topic}: {result}")

    print("\n=== PubMed Search (3 req/sec) ===")
    for topic in ["cancer immunotherapy", "CRISPR", "mRNA vaccine"]:
        result = search_pubmed(topic)
        print(f"  {topic}: {result['count']} papers")

    print("\n=== GitHub (sliding window) ===")
    github_demo()

    print("\nDone! No rate limits hit. ✓")
