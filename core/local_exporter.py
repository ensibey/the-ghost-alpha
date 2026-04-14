import os
import json
from datetime import datetime

# In GitHub Actions, use the workspace; locally use Desktop
SIGNALS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "signals")


def ensure_dir():
    """Ensure the signals output directory exists."""
    os.makedirs(SIGNALS_DIR, exist_ok=True)


def export_signal(signal_data: dict):
    """
    Save a standardized intelligence signal as a JSON file.
    Filename format: {category}_{timestamp}.json
    """
    ensure_dir()
    category = signal_data.get("category", "Unknown").replace(" ", "_").replace("/", "-")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:20]
    filename = f"{category}_{ts}.json"
    filepath = os.path.join(SIGNALS_DIR, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(signal_data, f, ensure_ascii=False, indent=2)
        strength = signal_data.get("signal_strength", 0)
        title = signal_data.get("data", {}).get("title", "N/A")
        print(f"[Exporter] ✅ Saved: {filename} | Score: {strength} | {title}")
    except Exception as e:
        print(f"[Exporter] ❌ Failed to save signal: {e}")


def export_batch(signals: list):
    """Export a list of signal dicts."""
    for s in signals:
        export_signal(s)
