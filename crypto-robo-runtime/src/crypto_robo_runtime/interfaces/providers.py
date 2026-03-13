"""Protocols for providers and persistence layers."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from crypto_robo_runtime.domain.models import (
    AssetListing,
    ExecutedOrder,
    ExecutionReport,
    FeatureSnapshot,
    Holding,
    ProposedOrder,
    RebalancePlan,
    ResearchMemo,
)


class MarketDataProvider(Protocol):
    """Provider for ranked assets, exchange mappings, and features."""

    def list_assets(self, as_of: datetime) -> list[AssetListing]:
        """Return ranked and enriched asset listings."""
        ...

    def get_features(self, symbols: list[str], as_of: datetime) -> list[FeatureSnapshot]:
        """Return strategy features for the requested symbols."""
        ...


class ExchangeAdapter(Protocol):
    """Adapter for execution venue balances and order handling."""

    def list_holdings(self) -> list[Holding]:
        """Return current positions and quote balances."""
        ...

    def preview_order(self, order: ProposedOrder) -> ExecutedOrder:
        """Preview an order without sending it."""
        ...

    def place_order(self, order: ProposedOrder) -> ExecutedOrder:
        """Submit a live order to the exchange."""
        ...


class ResearchOverlayProvider(Protocol):
    """Provider for AI market memo and bounded risk multiplier."""

    def generate_memo(self, as_of: datetime) -> ResearchMemo:
        """Return a structured market memo."""
        ...


class StateStore(Protocol):
    """Persistence layer for plans, reports, and idempotency markers."""

    def save_rebalance_plan(self, plan: RebalancePlan) -> None:
        """Persist a rebalance plan."""
        ...

    def save_execution_report(self, report: ExecutionReport) -> None:
        """Persist an execution report."""
        ...

    def record_audit_event(self, event_type: str, payload: dict[str, object]) -> None:
        """Persist a lightweight audit event."""
        ...

    def has_idempotency_key(self, key: str) -> bool:
        """Return whether a key was already processed."""
        ...

    def save_idempotency_key(self, key: str) -> None:
        """Persist a processed idempotency key."""
        ...
