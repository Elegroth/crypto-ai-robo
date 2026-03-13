"""Backtest scaffolding shared by research experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestScenario:
    """Minimal backtest metadata for future experiment runners."""

    name: str
    description: str
    lookback_days: int


def default_scenarios() -> list[BacktestScenario]:
    """Return the starter scenario set for the MVP research workspace."""

    return [
        BacktestScenario(
            name="weekly-large-cap",
            description="Weekly rebalance of top ranked large-cap assets with capped weights.",
            lookback_days=365,
        )
    ]
