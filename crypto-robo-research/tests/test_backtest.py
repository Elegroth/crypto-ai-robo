from crypto_robo_research.backtest import default_scenarios


def test_default_scenarios_include_weekly_large_cap() -> None:
    scenarios = default_scenarios()

    assert scenarios[0].name == "weekly-large-cap"
    assert scenarios[0].lookback_days == 365
