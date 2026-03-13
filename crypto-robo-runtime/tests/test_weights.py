from datetime import datetime, timezone

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import FeatureSnapshot
from crypto_robo_runtime.portfolio.weights import compute_target_weights


def _feature(symbol: str, momentum: float, volatility: float) -> FeatureSnapshot:
    return FeatureSnapshot(
        asset_id=symbol.lower(),
        symbol=symbol,
        as_of=datetime.now(timezone.utc),
        price_usd=100.0,
        momentum_30d=momentum,
        momentum_90d=momentum,
        momentum_180d=momentum,
        realized_vol_30d=volatility,
        max_drawdown_180d=-0.10,
        volume_24h_usd=5_000_000.0,
        btc_regime_signal=1.0,
    )


def test_compute_target_weights_caps_assets_and_reserves_cash() -> None:
    settings = AppSettings(
        TARGET_ASSET_COUNT=3,
        MAX_ASSET_WEIGHT=0.40,
        AI_RISK_MIN=0.50,
        AI_RISK_MAX=1.00,
        QUOTE_SYMBOL="USD",
    )
    targets = compute_target_weights(
        [
            _feature("BTC", 0.9, 0.25),
            _feature("ETH", 0.8, 0.35),
            _feature("SOL", 0.7, 0.45),
        ],
        settings,
        ai_multiplier=0.75,
    )

    weights = {target.symbol: target.target_weight for target in targets}

    assert round(sum(weights.values()), 8) == 1.0
    assert weights["USD"] == 0.25
    assert all(weight <= 0.40 for symbol, weight in weights.items() if symbol != "USD")


def test_compute_target_weights_defaults_to_cash_when_no_positive_scores() -> None:
    settings = AppSettings(QUOTE_SYMBOL="USD")
    targets = compute_target_weights([_feature("ADA", -0.2, 0.8)], settings, ai_multiplier=0.5)

    assert len(targets) == 1
    assert targets[0].symbol == "USD"
    assert targets[0].target_weight == 1.0
