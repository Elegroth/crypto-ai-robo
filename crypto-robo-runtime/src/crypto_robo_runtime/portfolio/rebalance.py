"""Rebalance planning helpers."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import (
    ExchangeName,
    Holding,
    PortfolioTarget,
    ProposedOrder,
    RebalancePlan,
)


def generate_rebalance_plan(
    holdings: list[Holding],
    targets: list[PortfolioTarget],
    settings: AppSettings,
    ai_multiplier: float,
    as_of: datetime,
) -> RebalancePlan:
    """Create a rebalance plan by comparing current holdings to targets."""

    total_value = sum(holding.market_value_usd for holding in holdings)
    if total_value <= 0:
        total_value = 1.0

    current_weights = {
        holding.symbol: holding.market_value_usd / total_value
        for holding in holdings
    }
    target_weights = {target.symbol: target.target_weight for target in targets}

    symbols = {
        symbol
        for symbol in set(current_weights) | set(target_weights)
        if symbol != settings.quote_symbol
    }

    draft_orders: list[ProposedOrder] = []
    for symbol in sorted(symbols):
        target_weight = target_weights.get(symbol, 0.0)
        current_weight = current_weights.get(symbol, 0.0)
        drift = target_weight - current_weight
        if abs(drift) < settings.drift_threshold:
            continue

        draft_orders.append(
            ProposedOrder(
                symbol=symbol,
                side="buy" if drift > 0 else "sell",
                notional_usd=round(abs(drift) * total_value, 2),
                reason="weekly_rebalance",
            )
        )

    scaled_orders = _apply_order_caps(
        orders=draft_orders,
        total_value=total_value,
        turnover_cap=settings.turnover_cap,
        max_daily_notional_usd=settings.max_daily_notional_usd,
    )
    actual_turnover = sum(order.notional_usd for order in scaled_orders) / total_value

    return RebalancePlan(
        plan_id=f"plan-{uuid4()}",
        as_of=as_of,
        exchange=ExchangeName(settings.active_exchange),
        targets=targets,
        orders=scaled_orders,
        total_turnover=min(actual_turnover, 1.0),
        ai_multiplier=ai_multiplier,
        live_trading_enabled=settings.live_trading,
        warnings=[],
    )


def _apply_order_caps(
    orders: list[ProposedOrder],
    total_value: float,
    turnover_cap: float,
    max_daily_notional_usd: float,
) -> list[ProposedOrder]:
    """Scale proposed orders so they fit turnover and daily notional limits."""

    if not orders:
        return []

    total_notional = sum(order.notional_usd for order in orders)
    turnover_scale = (
        min(1.0, (turnover_cap * total_value) / total_notional)
        if total_notional > 0
        else 1.0
    )
    notional_scale = (
        min(1.0, max_daily_notional_usd / total_notional)
        if total_notional > 0
        else 1.0
    )
    scale = min(turnover_scale, notional_scale)
    if scale <= 0.0:
        return []

    scaled_orders: list[ProposedOrder] = []
    for order in orders:
        scaled_notional = round(order.notional_usd * scale, 2)
        if scaled_notional <= 0.0:
            continue
        scaled_orders.append(
            ProposedOrder(
                symbol=order.symbol,
                side=order.side,
                notional_usd=scaled_notional,
                reason=order.reason,
            )
        )
    return scaled_orders
