"""Render human-readable plan summaries."""

from __future__ import annotations

from crypto_robo_runtime.domain.models import RebalancePlan, ResearchMemo


def render_rebalance_summary(plan: RebalancePlan, memo: ResearchMemo) -> str:
    """Render a markdown summary for operator review."""

    lines = [
        "# Weekly Rebalance Summary",
        "",
        f"- Plan ID: `{plan.plan_id}`",
        f"- Exchange: `{plan.exchange}`",
        f"- AI regime: `{memo.regime}` ({memo.multiplier:.2f}x)",
        f"- Orders: `{len(plan.orders)}`",
        f"- Total turnover: `{plan.total_turnover:.2%}`",
        "",
        "## Orders",
    ]
    if not plan.orders:
        lines.append("- No trades required.")
    else:
        lines.extend(
            [
                f"- `{order.side.upper()}` `{order.symbol}` for `${order.notional_usd:.2f}`"
                for order in plan.orders
            ]
        )

    lines.extend(["", "## Memo", memo.summary])
    return "\n".join(lines)
