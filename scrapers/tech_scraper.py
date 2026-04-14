"""
Tech Scraper — Category: Software / "The Early Adopter Alpha"
Sources:
  - GitHub API: Repos created in last 24h with 100+ stars
  - HuggingFace API: Newest trending models by downloads
  - Product Hunt: High upvote-velocity products (Playwright fallback)
"""
import os
import time
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS_GH = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "X-GitHub-Api-Version": "2022-11-28"
}


def scrape_github_trending() -> List[Dict]:
    """Repos created in last 24h that already have 100+ stars — early movers."""
    since = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d")
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=created:>{since}+stars:>100&sort=stars&order=desc&per_page=10"
    )
    try:
        resp = requests.get(url, headers=HEADERS_GH, timeout=15)
        if resp.status_code != 200:
            print(f"[GitHub API] Error {resp.status_code}: {resp.text[:200]}")
            return []
        items = resp.json().get("items", [])
        results = []
        for repo in items:
            results.append({
                "title": repo.get("full_name", ""),
                "source": "GitHub",
                "source_url": repo.get("html_url", ""),
                "description": repo.get("description", "No description"),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language", "Unknown"),
                "topics": ", ".join(repo.get("topics", [])),
                "created_at": repo.get("created_at", ""),
            })
        print(f"[GitHub API] {len(results)} trending repos found.")
        return results
    except Exception as e:
        print(f"[GitHub API] Exception: {e}")
        return []


def scrape_huggingface_trending() -> List[Dict]:
    """Latest AI models sorted by monthly downloads."""
    url = "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=10&full=false"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        models = resp.json()
        results = []
        for m in models:
            results.append({
                "title": m.get("id", ""),
                "source": "HuggingFace",
                "source_url": f"https://huggingface.co/{m.get('id', '')}",
                "description": f"Task: {m.get('pipeline_tag', 'N/A')} | Downloads: {m.get('downloads', 0):,}",
                "downloads": m.get("downloads", 0),
                "likes": m.get("likes", 0),
                "tags": ", ".join(m.get("tags", [])[:5]),
            })
        print(f"[HuggingFace API] {len(results)} models found.")
        return results
    except Exception as e:
        print(f"[HuggingFace API] Exception: {e}")
        return []


def scrape_producthunt_trending() -> List[Dict]:
    """Product Hunt top products of the day via public API."""
    # Product Hunt has a GraphQL API that works without auth for basic queries
    url = "https://api.producthunt.com/v2/api/graphql"
    query = """
    {
      posts(order: VOTES, first: 10) {
        edges {
          node {
            name
            tagline
            votesCount
            url
            topics { edges { node { name } } }
          }
        }
      }
    }
    """
    try:
        resp = requests.post(url, json={"query": query}, timeout=15)
        if resp.status_code != 200:
            return []
        edges = resp.json().get("data", {}).get("posts", {}).get("edges", [])
        results = []
        for edge in edges:
            node = edge.get("node", {})
            topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
            results.append({
                "title": node.get("name", ""),
                "source": "Product Hunt",
                "source_url": node.get("url", ""),
                "description": node.get("tagline", ""),
                "votes": node.get("votesCount", 0),
                "topics": ", ".join(topics),
            })
        print(f"[Product Hunt API] {len(results)} products found.")
        return results
    except Exception as e:
        print(f"[Product Hunt API] Exception: {e}")
        return []


def get_tech_signals() -> str:
    """Aggregate all tech intelligence sources into a single text block for AI."""
    all_data = []
    all_data.extend(scrape_github_trending())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_huggingface_trending())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_producthunt_trending())

    if not all_data:
        return "No tech signals retrieved."

    lines = ["=== TECH / SOFTWARE MARKET INTELLIGENCE ==="]
    for item in all_data:
        lines.append(f"\n[{item['source']}] {item['title']}")
        lines.append(f"  URL: {item.get('source_url', 'N/A')}")
        lines.append(f"  Info: {item.get('description', '')}")
        if "stars" in item:
            lines.append(f"  Stars (24h): {item['stars']}")
        if "downloads" in item:
            lines.append(f"  Downloads: {item['downloads']:,}")
        if "votes" in item:
            lines.append(f"  Votes: {item['votes']}")
        if "language" in item:
            lines.append(f"  Language: {item['language']} | Topics: {item.get('topics','')}")

    return "\n".join(lines)
