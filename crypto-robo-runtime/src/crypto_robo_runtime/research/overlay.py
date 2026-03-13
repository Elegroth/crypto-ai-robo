"""AI research overlay helpers."""

from __future__ import annotations

from datetime import datetime

from crypto_robo_runtime.config.settings import AppSettings
from crypto_robo_runtime.domain.models import ResearchMemo, RiskRegime


def normalize_research_memo(memo: ResearchMemo, settings: AppSettings) -> ResearchMemo:
    """Clamp risky memo outputs into the configured safe envelope."""

    regime = memo.regime
    multiplier = memo.multiplier
    if memo.confidence < 0.4:
        regime = RiskRegime.NEUTRAL
        multiplier = settings.ai_default_multiplier

    multiplier = min(max(multiplier, settings.ai_risk_min), settings.ai_risk_max)
    return ResearchMemo(
        as_of=memo.as_of,
        regime=regime,
        confidence=memo.confidence,
        multiplier=multiplier,
        summary=memo.summary,
        rationale=memo.rationale,
        sources=memo.sources,
    )


class StaticResearchOverlayProvider:
    """Deterministic memo provider for development and tests."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def generate_memo(self, as_of: datetime) -> ResearchMemo:
        """Return a neutral memo when no external AI system is configured."""

        return ResearchMemo(
            as_of=as_of,
            regime=RiskRegime.NEUTRAL,
            confidence=1.0,
            multiplier=self._settings.ai_default_multiplier,
            summary="No external research provider configured; using neutral overlay.",
            rationale=["Default neutral stance for safe execution."],
            sources=["static://default"],
        )
