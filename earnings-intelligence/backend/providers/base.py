from abc import ABC, abstractmethod
from typing import Any


class PriceProvider(ABC):
    @abstractmethod
    def get_price_history(self, ticker: str, period: str = "1y") -> dict: ...

    @abstractmethod
    def get_current_info(self, ticker: str) -> dict: ...

    @abstractmethod
    def get_post_earnings_reaction(self, ticker: str, earnings_date: str) -> dict: ...


class FilingsProvider(ABC):
    @abstractmethod
    def get_8k_filings(self, ticker: str, years_back: int = 3) -> list[dict]: ...

    @abstractmethod
    def get_filing_text(self, url: str) -> str: ...


class NewsProvider(ABC):
    @abstractmethod
    def get_articles(self, ticker: str, company_name: str, years_back: int = 3) -> list[dict]: ...


class RatingsProvider(ABC):
    @abstractmethod
    def get_rating_changes(self, ticker: str) -> list[dict]: ...

    @abstractmethod
    def get_consensus(self, ticker: str) -> dict: ...
