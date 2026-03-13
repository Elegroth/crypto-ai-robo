"""In-memory state store implementation for tests and local development."""

from __future__ import annotations

from crypto_robo_runtime.domain.models import ExecutionReport, RebalancePlan


class InMemoryStateStore:
    """Simple persistence layer used for local iteration."""

    def __init__(self) -> None:
        self._plans: dict[str, RebalancePlan] = {}
        self._reports: dict[str, ExecutionReport] = {}
        self._audit: list[tuple[str, dict[str, object]]] = []
        self._idempotency: set[str] = set()

    def save_rebalance_plan(self, plan: RebalancePlan) -> None:
        """Persist a plan in memory."""

        self._plans[plan.plan_id] = plan

    def save_execution_report(self, report: ExecutionReport) -> None:
        """Persist a report in memory."""

        self._reports[report.plan_id] = report

    def record_audit_event(self, event_type: str, payload: dict[str, object]) -> None:
        """Persist a local audit event."""

        self._audit.append((event_type, payload))

    def has_idempotency_key(self, key: str) -> bool:
        """Return whether a key already exists."""

        return key in self._idempotency

    def save_idempotency_key(self, key: str) -> None:
        """Persist a key once processed."""

        self._idempotency.add(key)
