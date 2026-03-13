"""Lambda-friendly handlers for scheduled jobs."""

from __future__ import annotations

from datetime import UTC, datetime

from crypto_robo_runtime.audit.state import InMemoryStateStore
from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.data.coingecko import CoinGeckoProvider
from crypto_robo_runtime.execution.coinbase import CoinbaseAdvancedAdapter
from crypto_robo_runtime.execution.kraken import KrakenAdapter
from crypto_robo_runtime.interfaces.providers import ExchangeAdapter
from crypto_robo_runtime.orchestration.service import WeeklyRebalanceService
from crypto_robo_runtime.research.overlay import StaticResearchOverlayProvider


def weekly_rebalance_handler(event: dict[str, object], context: object) -> dict[str, object]:
    """Lambda entrypoint for the weekly rebalance job."""

    _ = context
    settings = AppSettings()
    market_data = CoinGeckoProvider()
    exchange: ExchangeAdapter
    if settings.active_exchange == "coinbase":
        exchange = CoinbaseAdvancedAdapter()
    else:
        exchange = KrakenAdapter()
    research = StaticResearchOverlayProvider(settings)
    state_store = InMemoryStateStore()
    service = WeeklyRebalanceService(
        settings=settings,
        market_data=market_data,
        exchange=exchange,
        research=research,
        state_store=state_store,
    )
    as_of = datetime.now(UTC)
    event_id = str(event.get("id", as_of.isoformat()))
    report, summary = service.run(as_of=as_of, idempotency_key=event_id)
    return {"status": report.status, "plan_id": report.plan_id, "summary": summary}
