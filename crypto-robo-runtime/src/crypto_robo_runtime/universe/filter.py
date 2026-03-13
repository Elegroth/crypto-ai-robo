"""Pure functions for investable universe selection."""

from __future__ import annotations

from datetime import datetime

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import AssetListing, ExchangeName, UniverseSnapshot


def build_universe(
    listings: list[AssetListing],
    exchange: ExchangeName,
    as_of: datetime,
    settings: AppSettings,
) -> UniverseSnapshot:
    """Filter listings into an approved investable universe."""

    ranked = sorted(
        listings,
        key=lambda item: item.market_cap_rank if item.market_cap_rank is not None else 10**9,
    )

    excluded_symbols: dict[str, str] = {}
    approved_assets: list[AssetListing] = []

    for listing in ranked:
        reason: str | None = None
        if listing.market_cap_rank is None or listing.market_cap_rank > settings.top_n_assets:
            reason = "outside_market_cap_threshold"
        elif listing.is_stablecoin:
            reason = "stablecoin_not_investable"
        elif listing.is_wrapped:
            reason = "wrapped_asset"
        elif listing.is_leveraged:
            reason = "leveraged_token"
        elif listing.volume_24h_usd < settings.min_volume_usd:
            reason = "insufficient_volume"
        elif not listing.tradable:
            reason = "not_tradable_on_exchange"

        if reason is not None:
            excluded_symbols[listing.symbol] = reason
            continue

        approved_assets.append(listing)

    return UniverseSnapshot(
        as_of=as_of,
        exchange=exchange,
        approved_assets=approved_assets,
        excluded_symbols=excluded_symbols,
    )
