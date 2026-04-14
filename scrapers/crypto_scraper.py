"""
Crypto Scraper — Category: Crypto / "On-Chain & Sentiment Signals"
Sources:
  - DexScreener API: Tokens with sudden volume/social spike
  - CoinGecko API: Trending coins (free, no auth needed)
  - DEXTools trending pairs (Playwright fallback)
"""
import time
import random
import requests
from typing import List, Dict


def scrape_dexscreener_trending() -> List[Dict]:
    """Tokens trending on DexScreener with high volume and price movement."""
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"[DexScreener] Error {resp.status_code}")
            return []
        tokens = resp.json() if isinstance(resp.json(), list) else []
        results = []
        for t in tokens[:15]:
            results.append({
                "title": t.get("tokenAddress", "Unknown"),
                "source": "DexScreener",
                "source_url": t.get("url", ""),
                "chain": t.get("chainId", "Unknown"),
                "description": t.get("description", ""),
                "contract_address": t.get("tokenAddress", ""),
            })
        print(f"[DexScreener] {len(results)} token profiles found.")
        return results
    except Exception as e:
        print(f"[DexScreener] Exception: {e}")
        return []


def scrape_dexscreener_gainers() -> List[Dict]:
    """Top gaining pairs in the last hour on all chains."""
    # Search for tokens with high price change
    url = "https://api.dexscreener.com/latest/dex/search?q=SOL"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        pairs = resp.json().get("pairs", [])
        # Sort by 24h price change descending
        pairs_sorted = sorted(
            [p for p in pairs if p.get("priceChange", {}).get("h24") is not None],
            key=lambda x: float(x.get("priceChange", {}).get("h24", 0) or 0),
            reverse=True
        )[:10]
        results = []
        for p in pairs_sorted:
            base = p.get("baseToken", {})
            price_change_h1 = p.get("priceChange", {}).get("h1", 0)
            price_change_h24 = p.get("priceChange", {}).get("h24", 0)
            volume_h24 = p.get("volume", {}).get("h24", 0)
            results.append({
                "title": f"{base.get('symbol', '?')} ({base.get('name', '?')})",
                "source": "DexScreener Gainers",
                "source_url": p.get("url", ""),
                "contract_address": base.get("address", ""),
                "chain": p.get("chainId", "Unknown"),
                "price_change_1h": price_change_h1,
                "price_change_24h": price_change_h24,
                "volume_24h": volume_h24,
                "liquidity_usd": p.get("liquidity", {}).get("usd", 0),
                "description": (
                    f"Price +{price_change_h1}% (1h), +{price_change_h24}% (24h) | "
                    f"Vol: ${volume_h24:,.0f} | Liq: ${p.get('liquidity',{}).get('usd',0):,.0f}"
                )
            })
        print(f"[DexScreener Gainers] {len(results)} pairs found.")
        return results
    except Exception as e:
        print(f"[DexScreener Gainers] Exception: {e}")
        return []


def scrape_coingecko_trending() -> List[Dict]:
    """CoinGecko's free trending endpoint — no API key needed."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"[CoinGecko] Error {resp.status_code}")
            return []
        coins = resp.json().get("coins", [])
        results = []
        for c in coins:
            item = c.get("item", {})
            results.append({
                "title": f"{item.get('symbol', '?')} — {item.get('name', '?')}",
                "source": "CoinGecko Trending",
                "source_url": f"https://www.coingecko.com/en/coins/{item.get('id', '')}",
                "contract_address": item.get("platforms", {}).get("ethereum", "N/A"),
                "market_cap_rank": item.get("market_cap_rank", "N/A"),
                "description": f"Trending rank #{item.get('score', '?')+1} on CoinGecko | Market cap rank: {item.get('market_cap_rank', 'N/A')}",
            })
        print(f"[CoinGecko] {len(results)} trending coins found.")
        return results
    except Exception as e:
        print(f"[CoinGecko] Exception: {e}")
        return []


def get_crypto_signals() -> str:
    """Aggregate all crypto intelligence into a single text block for AI."""
    all_data = []
    all_data.extend(scrape_dexscreener_trending())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_dexscreener_gainers())
    time.sleep(random.uniform(1, 2))
    all_data.extend(scrape_coingecko_trending())

    if not all_data:
        return "No crypto signals retrieved."

    lines = ["=== CRYPTO / WEB3 ON-CHAIN INTELLIGENCE ==="]
    for item in all_data:
        lines.append(f"\n[{item['source']}] {item['title']}")
        lines.append(f"  Chain: {item.get('chain', 'N/A')}")
        lines.append(f"  Contract: {item.get('contract_address', 'N/A')}")
        lines.append(f"  URL: {item.get('source_url', 'N/A')}")
        lines.append(f"  Info: {item.get('description', '')}")
        if "price_change_1h" in item:
            lines.append(f"  Price Change 1h: {item['price_change_1h']}% | 24h: {item['price_change_24h']}%")
        if "volume_24h" in item:
            lines.append(f"  Volume 24h: ${item['volume_24h']:,.0f}")

    return "\n".join(lines)
