from datetime import UTC, datetime

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import FeatureSnapshot, Holding
from crypto_robo_runtime.portfolio.rebalance import generate_rebalance_plan
from crypto_robo_runtime.portfolio.weights import compute_target_weights


def test_generate_rebalance_plan_respects_drift_threshold_and_notional_cap() -> None:
    settings = AppSettings(
        DRIFT_THRESHOLD=0.05,
        MAX_DAILY_NOTIONAL_USD=100.0,
        TURNOVER_CAP=0.20,
        QUOTE_SYMBOL="USD",
    )
    features = [
        FeatureSnapshot(
            asset_id="btc",
            symbol="BTC",
            as_of=datetime.now(UTC),
            price_usd=100.0,
            momentum_30d=0.9,
            momentum_90d=0.9,
            momentum_180d=0.9,
            realized_vol_30d=0.2,
            max_drawdown_180d=-0.1,
            volume_24h_usd=5_000_000,
            btc_regime_signal=1.0,
        )
    ]
    holdings = [
        Holding(symbol="BTC", quantity=1.0, market_value_usd=40.0),
        Holding(
            symbol="USD",
            quantity=60.0,
            market_value_usd=60.0,
            is_quote_asset=True,
        ),
    ]
    targets = compute_target_weights(features, settings, ai_multiplier=1.0)

    plan = generate_rebalance_plan(
        holdings,
        targets,
        settings,
        ai_multiplier=1.0,
        as_of=datetime.now(UTC),
    )

    assert len(plan.orders) == 1
    assert plan.orders[0].symbol == "BTC"
    assert plan.orders[0].notional_usd <= 20.0


def test_generate_rebalance_plan_sells_assets_missing_from_targets() -> None:
    settings = AppSettings(
        DRIFT_THRESHOLD=0.01,
        MAX_DAILY_NOTIONAL_USD=1_000.0,
        TURNOVER_CAP=1.0,
        QUOTE_SYMBOL="USD",
    )
    holdings = [
        Holding(symbol="DOGE", quantity=100.0, market_value_usd=50.0),
        Holding(
            symbol="USD",
            quantity=50.0,
            market_value_usd=50.0,
            is_quote_asset=True,
        ),
    ]

    plan = generate_rebalance_plan(
        holdings,
        [],
        settings,
        ai_multiplier=0.5,
        as_of=datetime.now(UTC),
    )

    assert len(plan.orders) == 1
    assert plan.orders[0].symbol == "DOGE"
    assert plan.orders[0].side == "sell"
