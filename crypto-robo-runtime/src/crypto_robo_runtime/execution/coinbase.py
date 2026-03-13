"""Coinbase Advanced adapter stub."""

from __future__ import annotations

from crypto_robo_runtime.domain.models import ExecutedOrder, Holding, ProposedOrder


class CoinbaseAdvancedAdapter:
    """Stub adapter for Coinbase Advanced."""

    def list_holdings(self) -> list[Holding]:
        """Return portfolio holdings from Coinbase."""

        return []

    def preview_order(self, order: ProposedOrder) -> ExecutedOrder:
        """Return a preview response."""

        return ExecutedOrder(symbol=order.symbol, side=order.side, status="previewed")

    def place_order(self, order: ProposedOrder) -> ExecutedOrder:
        """Return a stub submitted response."""

        return ExecutedOrder(symbol=order.symbol, side=order.side, status="submitted")
