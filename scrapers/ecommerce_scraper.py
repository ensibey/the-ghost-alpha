"""
E-Commerce Scraper — Category: E-Commerce / "Viral Product Prediction"
Sources:
  - Reddit API (r/NewProductPorn, r/SpecializedTools): "Where can I buy?" posts
  - Pinterest Trends (Playwright): Search-spiking items
  - AliExpress search (Playwright): Supplier price discovery
"""
import os
import time
import random
import requests
from typing import List, Dict


REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "GhostAlpha/2.0 by ensibey"

SUBREDDITS = [
    "NewProductPorn",
    "SpecializedTools",
    "Entrepreneur",
    "shutupandtakemymoney",
]


def get_reddit_token() -> str:
    """Get Reddit OAuth token if credentials are available."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return ""
    try:
        auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": REDDIT_USER_AGENT}
        resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth, data=data, headers=headers, timeout=10
        )
        return resp.json().get("access_token", "")
    except Exception:
        return ""


def scrape_reddit_products() -> List[Dict]:
    """Scrape Reddit for viral product discussions using public JSON endpoints."""
    results = []
    token = get_reddit_token()
    headers = {
        "User-Agent": REDDIT_USER_AGENT,
        **({"Authorization": f"Bearer {token}"} if token else {})
    }
    base_url = "https://oauth.reddit.com" if token else "https://www.reddit.com"

    for sub in SUBREDDITS:
        try:
            url = f"{base_url}/r/{sub}/hot.json?limit=10"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                # Fallback to public endpoint
                resp = requests.get(
                    f"https://www.reddit.com/r/{sub}/hot.json?limit=10",
                    headers={"User-Agent": REDDIT_USER_AGENT},
                    timeout=15
                )
            if resp.status_code != 200:
                continue
            posts = resp.json().get("data", {}).get("children", [])
            for post in posts:
                d = post.get("data", {})
                # Filter for posts with meaningful engagement
                if d.get("score", 0) < 50:
                    continue
                results.append({
                    "title": d.get("title", ""),
                    "source": f"Reddit r/{sub}",
                    "source_url": f"https://reddit.com{d.get('permalink', '')}",
                    "description": (
                        f"Score: {d.get('score',0)} | Comments: {d.get('num_comments',0)} | "
                        f"Subreddit: r/{sub}"
                    ),
                    "score": d.get("score", 0),
                    "comments": d.get("num_comments", 0),
                    "url": d.get("url", ""),
                    "selftext": d.get("selftext", "")[:300],
                })
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            print(f"[Reddit r/{sub}] Exception: {e}")

    print(f"[Reddit] {len(results)} posts scraped across {len(SUBREDDITS)} subreddits.")
    return results


def scrape_pinterest_trends() -> List[Dict]:
    """Pinterest trending topics via unofficial trends endpoint."""
    try:
        url = "https://trends.pinterest.com/api/v1/?country_code=US&limit=20"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://trends.pinterest.com/",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[Pinterest] Error {resp.status_code}, skipping.")
            return []
        data = resp.json()
        trends = data.get("trends", [])
        results = []
        for t in trends[:10]:
            term = t.get("term", "")
            growth = t.get("growth_rate", 0)
            results.append({
                "title": term,
                "source": "Pinterest Trends",
                "source_url": f"https://www.pinterest.com/search/pins/?q={term.replace(' ', '+')}",
                "description": f"Search growth rate: +{growth}% | Niche product opportunity",
                "growth_rate": growth,
            })
        print(f"[Pinterest] {len(results)} trends found.")
        return results
    except Exception as e:
        print(f"[Pinterest] Exception: {e}")
        return []


def get_ecommerce_signals() -> str:
    """Aggregate all e-commerce intelligence into a single text block for AI."""
    all_data = []
    all_data.extend(scrape_reddit_products())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_pinterest_trends())

    if not all_data:
        return "No e-commerce signals retrieved."

    lines = ["=== E-COMMERCE / VIRAL PRODUCT INTELLIGENCE ==="]
    for item in all_data:
        lines.append(f"\n[{item['source']}] {item['title']}")
        lines.append(f"  URL: {item.get('source_url', 'N/A')}")
        lines.append(f"  Info: {item.get('description', '')}")
        if "score" in item:
            lines.append(f"  Reddit Score: {item['score']} | Comments: {item['comments']}")
        if "growth_rate" in item:
            lines.append(f"  Pinterest Growth: +{item['growth_rate']}%")
        if item.get("selftext"):
            lines.append(f"  Context: {item['selftext'][:200]}...")

    return "\n".join(lines)
