import os
import time
import json
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Process, Task

# Core
from core.local_exporter import export_signal
from core.database import save_to_db

# Scrapers
from scrapers.tech_scraper import get_tech_signals
from scrapers.crypto_scraper import get_crypto_signals
from scrapers.ecommerce_scraper import get_ecommerce_signals
from scrapers.b2b_scraper import get_b2b_signals

# Agents
from agents.analyzer_agent import (
    create_tech_analyzer,
    create_crypto_analyzer,
    create_ecommerce_analyzer,
    create_b2b_analyzer,
)
from agents.strategist_agent import create_strategist_agent
from agents.writer_agent import create_writer_agent
from agents.models import IntelligenceOutput


# ──────────────────────────────────────────────────
# CATEGORY REGISTRY
# Each entry: (category_name, scraper_fn, analyzer_factory)
# ──────────────────────────────────────────────────
CATEGORY_REGISTRY = [
    ("Software",    get_tech_signals,       create_tech_analyzer),
    ("Crypto",      get_crypto_signals,     create_crypto_analyzer),
    ("E-Commerce",  get_ecommerce_signals,  create_ecommerce_analyzer),
    ("B2B",         get_b2b_signals,        create_b2b_analyzer),
]


def process_category(category_name: str, scraper_fn, analyzer_factory) -> list:
    """
    Run the full intelligence pipeline for one category.
    Returns a list of valid IntelligenceOutput dicts.
    """
    print(f"\n[⚡ START] {category_name} pipeline firing...")

    # 1. Scrape data
    try:
        raw_data = scraper_fn()
    except Exception as e:
        print(f"[{category_name}] Scraper failed: {e}")
        return []

    if not raw_data or raw_data.strip().startswith("No "):
        print(f"[{category_name}] No data retrieved. Skipping.")
        return []

    # 2. Build agents (fresh per run → no memory bleed between threads)
    analyzer = analyzer_factory()
    strategist = create_strategist_agent()
    writer = create_writer_agent()

    # 3. Define tasks
    analyze_task = Task(
        description=(
            f"You are analyzing {category_name} market intelligence data.\n\n"
            f"RAW DATA:\n{raw_data}\n\n"
            f"Your job: Filter noise, identify the TOP 3 most significant signals in this data. "
            f"For each signal, explain what it is and why it matters RIGHT NOW. "
            f"If everything is noise, say 'NO SIGNALS FOUND'."
        ),
        expected_output=(
            "A numbered list of up to 3 high-quality signals, each with: "
            "Signal name, why it's significant, and the source URL."
        ),
        agent=analyzer,
    )

    strategy_task = Task(
        description=(
            f"Take the {category_name} signals identified by the analyst. "
            f"For each signal:\n"
            f"1. Assign a signal_strength score (1.0-10.0) using the strict scoring criteria in your instructions.\n"
            f"2. Write one concrete action_tip sentence.\n"
            f"3. Identify the category as: {category_name}\n"
            f"If the analyst found no signals, output signal_strength 1.0 and minimal data."
        ),
        expected_output=(
            "For each signal: signal_strength score with justification, and a single action_tip sentence."
        ),
        agent=strategist,
        context=[analyze_task],
    )

    packaging_task = Task(
        description=(
            f"Package each scored {category_name} signal into the exact IntelligenceOutput schema. "
            f"Rules:\n"
            f"- category MUST be exactly: '{category_name}'\n"
            f"- timestamp MUST be current UTC time\n"
            f"- signal_strength MUST match the strategist's score\n"
            f"- data.title: short name (max 60 chars)\n"
            f"- data.source: platform name only\n"
            f"- data.insight: exactly 15-25 words explaining the significance\n"
            f"- action_tip: single sentence, direct imperative\n"
            f"Package the SINGLE BEST signal if multiple exist."
        ),
        expected_output="A single valid IntelligenceOutput JSON object.",
        agent=writer,
        output_pydantic=IntelligenceOutput,
        context=[analyze_task, strategy_task],
    )

    # 4. Run the crew
    crew = Crew(
        agents=[analyzer, strategist, writer],
        tasks=[analyze_task, strategy_task, packaging_task],
        process=Process.sequential,
        verbose=False,
    )

    results = []
    try:
        output = crew.kickoff()
        if output.pydantic:
            signal_dict = output.pydantic.dict()
            strength = float(signal_dict.get("signal_strength", 0))
            print(f"[{category_name}] ✅ Signal packaged. Score: {strength}/10")

            # 5. Export & notify
            export_signal(signal_dict)
            save_to_db("intelligence_signals", {"data": signal_dict})
            results.append(signal_dict)
        else:
            print(f"[{category_name}] No valid structured output produced.")
    except Exception as e:
        print(f"[{category_name}] Pipeline error: {e}")

    return results


def run_one_cycle():
    """Run all 4 category pipelines in parallel threads."""
    print(f"\n{'='*60}")
    print(f"  CYCLE START — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*60}")

    all_signals = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_category, name, scraper, analyzer): name
            for name, scraper, analyzer in CATEGORY_REGISTRY
        }
        for future in concurrent.futures.as_completed(futures):
            category_name = futures[future]
            try:
                signals = future.result()
                all_signals.extend(signals)
            except Exception as e:
                print(f"[{category_name}] Unhandled thread error: {e}")

    strong = [s for s in all_signals if float(s.get("signal_strength", 0)) >= 8.0]
    print(f"\n{'='*60}")
    print(f"  CYCLE COMPLETE — {len(all_signals)} signals | {len(strong)} high-alpha (≥8)")
    print(f"{'='*60}\n")
    return all_signals


def main():
    print("=" * 60)
    print("  THE GHOST ALPHA v2.0 — CONTINUOUS INTELLIGENCE ENGINE")
    print("  Categories: Software | Crypto | E-Commerce | B2B")
    print("=" * 60)
    load_dotenv()

    # ── Continuous loop config ──
    start_time = time.time()
    max_duration_seconds = (5 * 3600) + (45 * 60)  # 5h 45m — safe GitHub Actions exit
    cycle_sleep_seconds = 180  # 3 minutes between cycles (anti-ban + rate limit)
    cycle_number = 1

    while True:
        elapsed = time.time() - start_time
        remaining_minutes = int((max_duration_seconds - elapsed) / 60)

        # Safe exit before GitHub Actions hard-kills the process
        if elapsed >= max_duration_seconds:
            print("\n[⏰ SYSTEM] 5h45m safe limit reached. Exiting cleanly.")
            print("[⏰ SYSTEM] Next GitHub Actions Cron will resume the watch.")
            break

        print(f"\n[🔥 CYCLE {cycle_number}] Starting... (Remaining safe window: {remaining_minutes} min)")
        run_one_cycle()

        print(f"[💤 SLEEP] {cycle_sleep_seconds // 60}m rest between cycles (rate-limit protection)...")
        time.sleep(cycle_sleep_seconds)
        cycle_number += 1

    print("\n" + "=" * 60)
    print("  GHOST ALPHA ENGINE SHUT DOWN CLEANLY.")
    print("=" * 60)


if __name__ == "__main__":
    main()
