from datetime import datetime, timezone

import pytest

from crypto_robo_runtime.audit.state import InMemoryStateStore
from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import (
    AssetListing,
    ExecutedOrder,
    FeatureSnapshot,
    Holding,
    ProposedOrder,
    ResearchMemo,
    RiskRegime,
)
from crypto_robo_runtime.orchestration.service import WeeklyRebalanceService


class StubMarketData:
    def list_assets(self, as_of: datetime) -> list[AssetListing]:
        _ = as_of
        return [
            AssetListing(
                asset_id="btc",
                symbol="BTC",
                name="Bitcoin",
                market_cap_rank=1,
                market_cap_usd=1_000_000_000,
                price_usd=50_000,
                volume_24h_usd=5_000_000,
                tradable=True,
            )
        ]

    def get_features(self, symbols: list[str], as_of: datetime) -> list[FeatureSnapshot]:
        _ = symbols
        return [
            FeatureSnapshot(
                asset_id="btc",
                symbol="BTC",
                as_of=as_of,
                price_usd=50_000,
                momentum_30d=0.9,
                momentum_90d=0.9,
                momentum_180d=0.9,
                realized_vol_30d=0.2,
                max_drawdown_180d=-0.1,
                volume_24h_usd=5_000_000,
                btc_regime_signal=1.0,
            )
        ]


class StubExchange:
    def __init__(self) -> None:
        self.preview_calls = 0

    def list_holdings(self) -> list[Holding]:
        return [Holding(symbol="USD", quantity=100.0, market_value_usd=100.0, is_quote_asset=True)]

    def preview_order(self, order: ProposedOrder) -> ExecutedOrder:
        self.preview_calls += 1
        return ExecutedOrder(symbol=order.symbol, side=order.side, status="previewed")

    def place_order(self, order: ProposedOrder) -> ExecutedOrder:
        return ExecutedOrder(symbol=order.symbol, side=order.side, status="submitted")


class StubResearch:
    def generate_memo(self, as_of: datetime) -> ResearchMemo:
        return ResearchMemo(
            as_of=as_of,
            regime=RiskRegime.NEUTRAL,
            confidence=1.0,
            multiplier=0.8,
            summary="Neutral stance.",
            rationale=["Base case."],
            sources=["stub://memo"],
        )


def test_weekly_rebalance_service_rejects_duplicate_idempotency_keys() -> None:
    settings = AppSettings(LIVE_TRADING=False, QUOTE_SYMBOL="USD")
    state_store = InMemoryStateStore()
    exchange = StubExchange()
    service = WeeklyRebalanceService(
        settings=settings,
        market_data=StubMarketData(),
        exchange=exchange,
        research=StubResearch(),
        state_store=state_store,
    )
    as_of = datetime.now(timezone.utc)

    report, _ = service.run(as_of=as_of, idempotency_key="dup-key")

    assert report.status == "preview_only"
    assert exchange.preview_calls == 1

    with pytest.raises(ValueError, match="idempotency key already processed"):
        service.run(as_of=as_of, idempotency_key="dup-key")
