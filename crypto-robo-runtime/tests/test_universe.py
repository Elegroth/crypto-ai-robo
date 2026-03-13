from datetime import UTC, datetime

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import AssetListing, ExchangeName
from crypto_robo_runtime.universe.filter import build_universe


def test_build_universe_excludes_non_investable_assets() -> None:
    settings = AppSettings(
        TOP_N_ASSETS=50,
        MIN_VOLUME_USD=1_000_000,
    )
    listings = [
        AssetListing(
            asset_id="btc",
            symbol="BTC",
            name="Bitcoin",
            market_cap_rank=1,
            market_cap_usd=1_000_000_000,
            price_usd=50_000,
            volume_24h_usd=5_000_000,
            tradable=True,
        ),
        AssetListing(
            asset_id="usdc",
            symbol="USDC",
            name="USD Coin",
            market_cap_rank=6,
            market_cap_usd=10_000_000,
            price_usd=1,
            volume_24h_usd=8_000_000,
            tradable=True,
            is_stablecoin=True,
        ),
        AssetListing(
            asset_id="lowvol",
            symbol="LOW",
            name="Low Volume",
            market_cap_rank=10,
            market_cap_usd=8_000_000,
            price_usd=10,
            volume_24h_usd=20_000,
            tradable=True,
        ),
    ]

    universe = build_universe(listings, ExchangeName.COINBASE, datetime.now(UTC), settings)

    assert [asset.symbol for asset in universe.approved_assets] == ["BTC"]
    assert universe.excluded_symbols["USDC"] == "stablecoin_not_investable"
    assert universe.excluded_symbols["LOW"] == "insufficient_volume"
