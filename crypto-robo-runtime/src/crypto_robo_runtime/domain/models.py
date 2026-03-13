"""Core models shared across the runtime."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ExchangeName(StrEnum):
    """Supported execution venues."""

    COINBASE = "coinbase"
    KRAKEN = "kraken"


class RiskRegime(StrEnum):
    """AI research overlay regimes."""

    RISK_ON = "risk_on"
    NEUTRAL = "neutral"
    RISK_OFF = "risk_off"


class AssetListing(BaseModel):
    """Market metadata used to determine investable assets."""

    asset_id: str
    symbol: str
    name: str
    market_cap_rank: int | None = None
    market_cap_usd: float
    price_usd: float
    volume_24h_usd: float
    is_stablecoin: bool = False
    is_wrapped: bool = False
    is_leveraged: bool = False
    tradable: bool = False


class FeatureSnapshot(BaseModel):
    """Point-in-time strategy features for one asset."""

    asset_id: str
    symbol: str
    as_of: datetime
    price_usd: float
    momentum_30d: float
    momentum_90d: float
    momentum_180d: float
    realized_vol_30d: float
    max_drawdown_180d: float
    volume_24h_usd: float
    btc_regime_signal: float = Field(ge=0.0, le=1.0)


class UniverseSnapshot(BaseModel):
    """Approved investable universe for a rebalance cycle."""

    as_of: datetime
    exchange: ExchangeName
    approved_assets: list[AssetListing]
    excluded_symbols: dict[str, str]


class Holding(BaseModel):
    """Current portfolio position."""

    symbol: str
    quantity: float
    market_value_usd: float
    is_quote_asset: bool = False


class PortfolioTarget(BaseModel):
    """Target portfolio weight and score for one asset."""

    symbol: str
    target_weight: float = Field(ge=0.0, le=1.0)
    score: float
    capped: bool = False


class ProposedOrder(BaseModel):
    """Generated order proposal after portfolio and risk checks."""

    symbol: str
    side: Literal["buy", "sell"]
    notional_usd: float = Field(gt=0.0)
    order_type: Literal["market"] = "market"
    reason: str


class ResearchMemo(BaseModel):
    """Structured AI memo that may adjust total risk exposure."""

    as_of: datetime
    regime: RiskRegime
    confidence: float = Field(ge=0.0, le=1.0)
    multiplier: float = Field(ge=0.0, le=1.0)
    summary: str
    rationale: list[str]
    sources: list[str]


class RebalancePlan(BaseModel):
    """Complete rebalance output for review or execution."""

    plan_id: str
    as_of: datetime
    exchange: ExchangeName
    targets: list[PortfolioTarget]
    orders: list[ProposedOrder]
    total_turnover: float = Field(ge=0.0, le=1.0)
    ai_multiplier: float = Field(ge=0.0, le=1.0)
    live_trading_enabled: bool
    warnings: list[str]


class ExecutedOrder(BaseModel):
    """Result of a live or previewed order submission."""

    symbol: str
    side: Literal["buy", "sell"]
    status: Literal["previewed", "submitted", "rejected", "filled"]
    external_order_id: str | None = None
    filled_notional_usd: float | None = None


class ExecutionReport(BaseModel):
    """Execution summary persisted for audit and reconciliation."""

    plan_id: str
    submitted_at: datetime
    exchange: ExchangeName
    orders: list[ExecutedOrder]
    status: Literal["preview_only", "submitted", "blocked"]
    notes: list[str]
