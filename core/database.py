"""
database.py — Supabase Integration
Scraped & analyzed intelligence signals are persisted to the 'opportunities' table.

Expected Supabase table schema (run this SQL in your Supabase SQL Editor):
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS opportunities (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    timestamp       TEXT,
    category        TEXT,
    signal_strength FLOAT,
    title           TEXT,
    source          TEXT,
    source_url      TEXT,
    insight         TEXT,
    action_tip      TEXT,
    growth_rate     TEXT,
    contract_address TEXT,
    whale_signal    BOOLEAN,
    risk_score      FLOAT,
    supply_link     TEXT,
    competitor      TEXT,
    company_name    TEXT,
    funding_amount  TEXT,
    decision_maker  TEXT,
    open_positions  TEXT,
    raw_json        JSONB
);
---------------------------------------------------------------------
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Singleton client — created once, reused across threads
_client: Client = None


def get_db_client() -> Client:
    """Returns a cached Supabase client. Skips gracefully if credentials missing."""
    global _client
    if _client:
        return _client
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def save_to_db(table_name: str, record_data: dict) -> dict:
    """
    Generic insert — kept for backward compatibility.
    Inserts raw dict into any given table.
    """
    db = get_db_client()
    if not db:
        print("[DB] Supabase credentials not set — skipping save.")
        return {}
    try:
        response = db.table(table_name).insert(record_data).execute()
        return response.data or {}
    except Exception as e:
        print(f"[DB] Insert error ({table_name}): {e}")
        return {"error": str(e)}


def save_opportunity(signal: dict) -> bool:
    """
    Flattens a standardized IntelligenceOutput dict and inserts it
    into the 'opportunities' table with each field in its own column.

    Args:
        signal: A dict matching the IntelligenceOutput schema.

    Returns:
        True if saved successfully, False otherwise.
    """
    db = get_db_client()
    if not db:
        print("[DB] Supabase credentials not set — opportunity not saved.")
        return False

    data = signal.get("data", {})

    # Flatten the nested structure into individual columns
    row = {
        "timestamp":        signal.get("timestamp"),
        "category":         signal.get("category"),
        "signal_strength":  signal.get("signal_strength"),
        "title":            data.get("title"),
        "source":           data.get("source"),
        "source_url":       data.get("source_url"),
        "insight":          data.get("insight"),
        "action_tip":       signal.get("action_tip"),
        # Optional category-specific fields
        "growth_rate":      data.get("growth_rate"),
        "contract_address": data.get("contract_address"),
        "whale_signal":     data.get("whale_signal"),
        "risk_score":       data.get("risk_score"),
        "supply_link":      data.get("supply_link"),
        "competitor":       data.get("competitor"),
        "company_name":     data.get("company_name"),
        "funding_amount":   data.get("funding_amount"),
        "decision_maker":   data.get("decision_maker"),
        "open_positions":   data.get("open_positions"),
        # Full raw JSON for debugging / future use
        "raw_json":         signal,
    }

    # Remove None values — Supabase will use column defaults
    row = {k: v for k, v in row.items() if v is not None}

    try:
        response = db.table("opportunities").insert(row).execute()
        title = data.get("title", "N/A")
        strength = signal.get("signal_strength", 0)
        print(f"[DB] ✅ Saved to Supabase: '{title}' | Score: {strength}")
        return True
    except Exception as e:
        print(f"[DB] ❌ Failed to save opportunity: {e}")
        return False
