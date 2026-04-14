from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SignalData(BaseModel):
    """Inner data payload — varies by category."""
    title: str = Field(description="Name of the repo, token, product or company.")
    source: str = Field(description="Platform the data was pulled from (e.g. GitHub, DexScreener, Reddit).")
    insight: str = Field(description="One concise sentence explaining WHY this is significant right now.")
    # Optional category-specific fields
    growth_rate: Optional[str] = Field(default=None, description="Growth % per hour or day where applicable.")
    contract_address: Optional[str] = Field(default=None, description="On-chain contract address for crypto signals.")
    whale_signal: Optional[bool] = Field(default=None, description="True if large wallet accumulation detected.")
    risk_score: Optional[float] = Field(default=None, description="Risk level 1-10. 10 = highest risk.", ge=1, le=10)
    supply_link: Optional[str] = Field(default=None, description="AliExpress or Alibaba supplier link for e-commerce signals.")
    competitor: Optional[str] = Field(default=None, description="Main competitor for tech/software signals.")
    company_name: Optional[str] = Field(default=None, description="Company name for B2B lead signals.")
    funding_amount: Optional[str] = Field(default=None, description="Latest funding round amount.")
    decision_maker: Optional[str] = Field(default=None, description="CEO or CTO name for B2B outreach.")
    open_positions: Optional[str] = Field(default=None, description="Job titles the company is actively hiring.")
    source_url: Optional[str] = Field(default=None, description="Direct link to the original signal.")


class IntelligenceOutput(BaseModel):
    """
    RapidAPI-Ready standardized output schema.
    Every signal produced by The Ghost Alpha MUST conform to this shape.
    If incoming data is noise, set signal_strength to 1 or below and leave data fields minimal.
    """
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        description="UTC timestamp of signal generation."
    )
    category: str = Field(
        description="One of: Software | Crypto | E-Commerce | B2B"
    )
    signal_strength: float = Field(
        description=(
            "Overall signal quality score 1.0-10.0. "
            "1-4: noise/weak, 5-7: moderate, 8-9: strong, 9.5-10: rare alpha. "
            "Only signals >= 8 get pushed to Telegram."
        ),
        ge=1.0, le=10.0
    )
    data: SignalData = Field(description="Category-specific structured payload.")
    action_tip: str = Field(
        description=(
            "A single, immediately actionable advice sentence. "
            "Written as if advising a smart investor or entrepreneur. "
            "Example: 'Buy domain {keyword}.io before it trends; high demand expected in Q3 2026.'"
        )
    )
