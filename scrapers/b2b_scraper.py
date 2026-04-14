"""
B2B Scraper — Category: B2B / "Lead & Job Market Signals"
Sources:
  - Indeed (Playwright): Companies hiring 10+ devs = growth signal
  - Crunchbase News RSS: Latest funding rounds
  - RemoteOK API: Booming hiring companies
"""
import time
import random
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict


def scrape_crunchbase_rss() -> List[Dict]:
    """Parse Crunchbase News RSS feed for latest funding round announcements."""
    url = "https://news.crunchbase.com/feed/"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GhostAlpha/2.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[Crunchbase RSS] Error {resp.status_code}")
            return []
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if not channel:
            return []
        items = channel.findall("item")
        results = []
        for item in items[:15]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()[:300]
            pub_date = item.findtext("pubDate", "")
            # Only include funding-related news
            keywords = ["funding", "raises", "series", "million", "billion", "seed", "venture", "backed"]
            if any(kw in title.lower() or kw in description.lower() for kw in keywords):
                results.append({
                    "title": title,
                    "source": "Crunchbase News",
                    "source_url": link,
                    "description": description,
                    "pub_date": pub_date,
                    "funding_amount": _extract_funding(title + " " + description),
                })
        print(f"[Crunchbase RSS] {len(results)} funding stories found.")
        return results
    except Exception as e:
        print(f"[Crunchbase RSS] Exception: {e}")
        return []


def _extract_funding(text: str) -> str:
    """Simple regex-free heuristic to extract funding amounts."""
    import re
    pattern = r'\$[\d.,]+\s*(?:million|billion|M|B)\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return ", ".join(matches) if matches else "Amount not specified"


def scrape_remoteok_jobs() -> List[Dict]:
    """RemoteOK public JSON API — identify companies on a major hiring spree."""
    url = "https://remoteok.com/api"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GhostAlpha/2.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[RemoteOK] Error {resp.status_code}")
            return []
        data = resp.json()
        if not isinstance(data, list):
            return []
        # Remove first element (it's legal/meta)
        jobs = [j for j in data if isinstance(j, dict) and j.get("company")]
        # Count jobs per company
        from collections import Counter
        company_counts = Counter(j.get("company", "") for j in jobs)
        # Focus on companies hiring 3+ roles simultaneously (growth signal)
        hot_companies = {c: cnt for c, cnt in company_counts.items() if cnt >= 3}
        results = []
        seen = set()
        for job in jobs:
            company = job.get("company", "")
            if company in hot_companies and company not in seen:
                seen.add(company)
                tags = job.get("tags", [])
                results.append({
                    "title": company,
                    "source": "RemoteOK",
                    "source_url": f"https://remoteok.com/remote-jobs?filter={company.replace(' ', '+')}",
                    "description": (
                        f"Hiring {hot_companies[company]} roles simultaneously — GROWTH SIGNAL. "
                        f"Example position: {job.get('position', 'Engineer')}. "
                        f"Tech stack: {', '.join(tags[:5]) if tags else 'N/A'}"
                    ),
                    "open_positions": f"{hot_companies[company]} open roles",
                    "company_name": company,
                })
        print(f"[RemoteOK] {len(results)} high-velocity hiring companies found.")
        return results[:10]
    except Exception as e:
        print(f"[RemoteOK] Exception: {e}")
        return []


def scrape_techcrunch_rss() -> List[Dict]:
    """TechCrunch RSS for startup funding news — additional layer."""
    url = "https://techcrunch.com/feed/"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; GhostAlpha/2.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if not channel:
            return []
        items = channel.findall("item")
        results = []
        for item in items[:10]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")[:300]
            keywords = ["funding", "raises", "series", "million", "startup", "venture"]
            if any(kw in title.lower() for kw in keywords):
                results.append({
                    "title": title,
                    "source": "TechCrunch",
                    "source_url": link,
                    "description": desc,
                    "funding_amount": _extract_funding(title + " " + desc),
                })
        print(f"[TechCrunch] {len(results)} funding articles found.")
        return results
    except Exception as e:
        print(f"[TechCrunch] Exception: {e}")
        return []


def get_b2b_signals() -> str:
    """Aggregate all B2B intelligence into a single text block for AI."""
    all_data = []
    all_data.extend(scrape_crunchbase_rss())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_remoteok_jobs())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_techcrunch_rss())

    if not all_data:
        return "No B2B signals retrieved."

    lines = ["=== B2B / LEAD & FUNDING INTELLIGENCE ==="]
    for item in all_data:
        lines.append(f"\n[{item['source']}] {item['title']}")
        lines.append(f"  URL: {item.get('source_url', 'N/A')}")
        lines.append(f"  Info: {item.get('description', '')}")
        if item.get("funding_amount"):
            lines.append(f"  Funding: {item['funding_amount']}")
        if item.get("open_positions"):
            lines.append(f"  Open Positions: {item['open_positions']}")

    return "\n".join(lines)
