from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    news_api_key: str = ""
    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite+aiosqlite:///./earnings_intelligence.db"

    price_provider: Literal["yahoo"] = "yahoo"
    filings_provider: Literal["edgar"] = "edgar"
    news_provider: Literal["newsapi"] = "newsapi"
    ratings_provider: Literal["yahoo"] = "yahoo"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

SECTOR_ETF_MAP = {
    "Technology": "XLK",
    "Communication Services": "XLC",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Financial Services": "XLF",
    "Healthcare": "XLV",
    "Industrials": "XLI",
    "Basic Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
}

PROVIDER_MAP = {
    "price": settings.price_provider,
    "filings": settings.filings_provider,
    "news": settings.news_provider,
    "ratings": settings.ratings_provider,
}
