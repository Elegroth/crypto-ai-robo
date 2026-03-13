"""CoinGecko market data provider stub."""

from __future__ import annotations

from datetime import datetime

from crypto_robo_runtime.domain.models import AssetListing, FeatureSnapshot


class CoinGeckoProvider:
    """Minimal provider stub for rankings and reference data."""

    def list_assets(self, as_of: datetime) -> list[AssetListing]:
        """Return rankings for the requested snapshot time."""

        _ = as_of
        return []

    def get_features(self, symbols: list[str], as_of: datetime) -> list[FeatureSnapshot]:
        """Return strategy features for the requested symbols."""

        _ = (symbols, as_of)
        return []
