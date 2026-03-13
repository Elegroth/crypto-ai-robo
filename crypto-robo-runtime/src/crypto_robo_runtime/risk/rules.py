"""Deterministic risk checks for rebalances and execution."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import FeatureSnapshot, ResearchMemo, RiskRegime


def validate_feature_freshness(
    features: list[FeatureSnapshot],
    settings: AppSettings,
    now: datetime,
) -> list[str]:
    """Return warnings for stale market data."""

    freshness_cutoff = now - timedelta(hours=settings.data_freshness_hours)
    return [
        f"stale_feature:{feature.symbol}"
        for feature in features
        if feature.as_of.replace(tzinfo=UTC)
        < freshness_cutoff.replace(tzinfo=UTC)
    ]


def validate_research_memo(
    memo: ResearchMemo,
    settings: AppSettings,
    now: datetime,
) -> list[str]:
    """Return warnings for stale or out-of-bounds research overlays."""

    warnings: list[str] = []
    freshness_cutoff = now - timedelta(hours=settings.research_freshness_hours)
    if memo.as_of.replace(tzinfo=UTC) < freshness_cutoff.replace(tzinfo=UTC):
        warnings.append("stale_research_memo")
    if not settings.ai_risk_min <= memo.multiplier <= settings.ai_risk_max:
        warnings.append("research_multiplier_out_of_bounds")
    if memo.confidence < 0.4 and memo.regime != RiskRegime.NEUTRAL:
        warnings.append("low_confidence_requires_neutral")
    return warnings


def validate_drawdown_limit(
    features: list[FeatureSnapshot],
    settings: AppSettings,
) -> list[str]:
    """Return warnings when assets breach the configured drawdown limit."""

    return [
        f"drawdown_limit_breached:{feature.symbol}"
        for feature in features
        if abs(min(feature.max_drawdown_180d, 0.0)) > settings.max_drawdown_limit
    ]
