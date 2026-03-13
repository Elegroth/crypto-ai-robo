"""Portfolio target generation helpers."""

from __future__ import annotations

from collections.abc import Iterable

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import FeatureSnapshot, PortfolioTarget
from crypto_robo_runtime.signals.scoring import compute_signal_score


def _apply_weight_caps(raw_weights: dict[str, float], max_weight: float) -> dict[str, float]:
    """Cap weights and redistribute excess until all weights respect the cap."""

    capped_weights = raw_weights.copy()
    while True:
        over_cap = {
            symbol: weight
            for symbol, weight in capped_weights.items()
            if weight > max_weight
        }
        if not over_cap:
            return capped_weights

        excess = sum(weight - max_weight for weight in over_cap.values())
        for symbol in over_cap:
            capped_weights[symbol] = max_weight

        under_cap = [symbol for symbol, weight in capped_weights.items() if weight < max_weight]
        if not under_cap or excess <= 0.0:
            return capped_weights

        redistribution_base = sum(capped_weights[symbol] for symbol in under_cap)
        if redistribution_base <= 0.0:
            equal_addition = excess / len(under_cap)
            for symbol in under_cap:
                capped_weights[symbol] += equal_addition
        else:
            for symbol in under_cap:
                capped_weights[symbol] += excess * (
                    capped_weights[symbol] / redistribution_base
                )


def compute_target_weights(
    features: Iterable[FeatureSnapshot],
    settings: AppSettings,
    ai_multiplier: float,
) -> list[PortfolioTarget]:
    """Build capped target weights with residual cash allocated to the quote asset."""

    scored_features = sorted(
        ((feature, compute_signal_score(feature)) for feature in features),
        key=lambda item: item[1],
        reverse=True,
    )
    winners = [item for item in scored_features[: settings.target_asset_count] if item[1] > 0.0]
    if not winners:
        return [
            PortfolioTarget(
                symbol=settings.quote_symbol,
                target_weight=1.0,
                score=0.0,
                capped=False,
            )
        ]

    inverse_vol_scores = {
        feature.symbol: max(score, 0.0) / max(feature.realized_vol_30d, 0.05)
        for feature, score in winners
    }
    total = sum(inverse_vol_scores.values())
    normalized = {symbol: value / total for symbol, value in inverse_vol_scores.items()}
    investable_budget = min(max(ai_multiplier, settings.ai_risk_min), settings.ai_risk_max)
    scaled = {symbol: weight * investable_budget for symbol, weight in normalized.items()}
    capped = _apply_weight_caps(scaled, settings.max_asset_weight)

    targets = [
        PortfolioTarget(
            symbol=feature.symbol,
            target_weight=round(capped[feature.symbol], 8),
            score=round(score, 8),
            capped=capped[feature.symbol] >= settings.max_asset_weight,
        )
        for feature, score in winners
    ]

    quote_weight = max(0.0, 1.0 - sum(target.target_weight for target in targets))
    targets.append(
        PortfolioTarget(
            symbol=settings.quote_symbol,
            target_weight=round(quote_weight, 8),
            score=0.0,
            capped=False,
        )
    )
    return sorted(targets, key=lambda item: item.target_weight, reverse=True)
