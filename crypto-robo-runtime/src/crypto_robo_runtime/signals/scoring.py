"""Signal scoring helpers."""

from __future__ import annotations

from crypto_robo_runtime.domain.models import FeatureSnapshot


def compute_signal_score(feature: FeatureSnapshot) -> float:
    """Return a deterministic score from momentum, volatility, and drawdown inputs."""

    momentum_component = (
        (feature.momentum_30d * 0.2)
        + (feature.momentum_90d * 0.5)
        + (feature.momentum_180d * 0.3)
    )
    volatility_penalty = feature.realized_vol_30d * 0.35
    drawdown_penalty = abs(min(feature.max_drawdown_180d, 0.0)) * 0.25
    regime_modifier = 0.5 + (feature.btc_regime_signal * 0.5)
    return (momentum_component - volatility_penalty - drawdown_penalty) * regime_modifier
