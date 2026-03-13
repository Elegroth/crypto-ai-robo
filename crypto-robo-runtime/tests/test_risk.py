from datetime import datetime, timedelta, timezone

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import FeatureSnapshot, ResearchMemo, RiskRegime
from crypto_robo_runtime.research.overlay import normalize_research_memo
from crypto_robo_runtime.risk.rules import validate_feature_freshness, validate_research_memo


def test_feature_freshness_warns_on_stale_data() -> None:
    settings = AppSettings(DATA_FRESHNESS_HOURS=24)
    feature = FeatureSnapshot(
        asset_id="btc",
        symbol="BTC",
        as_of=datetime.now(timezone.utc) - timedelta(hours=30),
        price_usd=100.0,
        momentum_30d=0.1,
        momentum_90d=0.1,
        momentum_180d=0.1,
        realized_vol_30d=0.2,
        max_drawdown_180d=-0.1,
        volume_24h_usd=1_000_000.0,
        btc_regime_signal=1.0,
    )

    warnings = validate_feature_freshness([feature], settings, datetime.now(timezone.utc))

    assert warnings == ["stale_feature:BTC"]


def test_low_confidence_research_defaults_to_neutral() -> None:
    settings = AppSettings(AI_DEFAULT_MULTIPLIER=0.8)
    memo = ResearchMemo(
        as_of=datetime.now(timezone.utc),
        regime=RiskRegime.RISK_ON,
        confidence=0.2,
        multiplier=1.0,
        summary="Conflicting research.",
        rationale=["Signals disagree."],
        sources=["example://source"],
    )

    normalized = normalize_research_memo(memo, settings)
    warnings = validate_research_memo(normalized, settings, datetime.now(timezone.utc))

    assert normalized.regime == RiskRegime.NEUTRAL
    assert normalized.multiplier == 0.8
    assert warnings == []
