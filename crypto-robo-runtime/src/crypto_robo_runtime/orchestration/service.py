"""Weekly rebalance orchestration service."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from crypto_robo_runtime.audit.reporting import render_rebalance_summary
from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import ExecutedOrder, ExecutionReport, ExchangeName
from crypto_robo_runtime.interfaces.providers import (
    ExchangeAdapter,
    MarketDataProvider,
    ResearchOverlayProvider,
    StateStore,
)
from crypto_robo_runtime.portfolio.rebalance import generate_rebalance_plan
from crypto_robo_runtime.portfolio.weights import compute_target_weights
from crypto_robo_runtime.research.overlay import normalize_research_memo
from crypto_robo_runtime.risk.rules import (
    validate_drawdown_limit,
    validate_feature_freshness,
    validate_research_memo,
)
from crypto_robo_runtime.universe.filter import build_universe


class WeeklyRebalanceService:
    """Coordinate a full weekly rebalance plan from providers and pure functions."""

    def __init__(
        self,
        settings: AppSettings,
        market_data: MarketDataProvider,
        exchange: ExchangeAdapter,
        research: ResearchOverlayProvider,
        state_store: StateStore,
    ) -> None:
        self._settings = settings
        self._market_data = market_data
        self._exchange = exchange
        self._research = research
        self._state_store = state_store

    def run(self, as_of: datetime, idempotency_key: str) -> tuple[ExecutionReport, str]:
        """Build a plan, run previews or submissions, and persist the results."""

        if self._state_store.has_idempotency_key(idempotency_key):
            raise ValueError(f"idempotency key already processed: {idempotency_key}")

        exchange_name = ExchangeName(self._settings.active_exchange)
        memo = normalize_research_memo(self._research.generate_memo(as_of), self._settings)
        listings = self._market_data.list_assets(as_of)
        universe = build_universe(listings, exchange_name, as_of, self._settings)
        features = self._market_data.get_features(
            [asset.symbol for asset in universe.approved_assets],
            as_of,
        )

        warnings: list[str] = []
        warnings.extend(validate_feature_freshness(features, self._settings, as_of))
        warnings.extend(validate_drawdown_limit(features, self._settings))
        warnings.extend(validate_research_memo(memo, self._settings, as_of))

        targets = compute_target_weights(features, self._settings, memo.multiplier)
        holdings = self._exchange.list_holdings()
        plan = generate_rebalance_plan(holdings, targets, self._settings, memo.multiplier, as_of)
        plan.warnings.extend(warnings)
        self._state_store.save_rebalance_plan(plan)

        executed_orders: list[ExecutedOrder] = []
        status: Literal["preview_only", "submitted", "blocked"]
        notes: list[str]
        if warnings:
            status = "blocked"
            notes = warnings
        else:
            for order in plan.orders:
                if self._settings.live_trading:
                    executed_orders.append(self._exchange.place_order(order))
                else:
                    executed_orders.append(self._exchange.preview_order(order))
            status = "submitted" if self._settings.live_trading else "preview_only"
            notes = []

        report = ExecutionReport(
            plan_id=plan.plan_id,
            submitted_at=as_of,
            exchange=exchange_name,
            orders=executed_orders,
            status=status,
            notes=notes,
        )
        self._state_store.save_execution_report(report)
        self._state_store.record_audit_event("weekly_rebalance", report.model_dump(mode="json"))
        self._state_store.save_idempotency_key(idempotency_key)
        return report, render_rebalance_summary(plan, memo)
