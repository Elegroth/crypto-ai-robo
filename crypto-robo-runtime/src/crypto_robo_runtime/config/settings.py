"""Application settings for the crypto robo runtime."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Environment-driven settings shared across handlers."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    active_exchange: str = Field(default="coinbase", alias="ACTIVE_EXCHANGE")
    live_trading: bool = Field(default=False, alias="LIVE_TRADING")
    quote_symbol: str = Field(default="USD", alias="QUOTE_SYMBOL")
    top_n_assets: int = Field(default=100, alias="TOP_N_ASSETS")
    target_asset_count: int = Field(default=10, alias="TARGET_ASSET_COUNT")
    max_asset_weight: float = Field(default=0.15, alias="MAX_ASSET_WEIGHT")
    drift_threshold: float = Field(default=0.02, alias="DRIFT_THRESHOLD")
    turnover_cap: float = Field(default=0.20, alias="TURNOVER_CAP")
    max_daily_notional_usd: float = Field(default=2500.0, alias="MAX_DAILY_NOTIONAL_USD")
    min_volume_usd: float = Field(default=1_000_000.0, alias="MIN_VOLUME_USD")
    max_drawdown_limit: float = Field(default=0.35, alias="MAX_DRAWDOWN_LIMIT")
    data_freshness_hours: int = Field(default=24, alias="DATA_FRESHNESS_HOURS")
    research_freshness_hours: int = Field(default=24, alias="RESEARCH_FRESHNESS_HOURS")
    ai_risk_min: float = Field(default=0.50, alias="AI_RISK_MIN")
    ai_risk_max: float = Field(default=1.00, alias="AI_RISK_MAX")
    ai_default_multiplier: float = Field(default=0.85, alias="AI_DEFAULT_MULTIPLIER")
    state_table_name: str = Field(default="crypto-robo-dev-state", alias="STATE_TABLE_NAME")
    reports_bucket: str = Field(default="crypto-robo-dev-reports", alias="REPORTS_BUCKET")
    coinbase_api_key_secret_arn: str = Field(default="", alias="COINBASE_API_KEY_SECRET_ARN")
    kraken_api_key_secret_arn: str = Field(default="", alias="KRAKEN_API_KEY_SECRET_ARN")
