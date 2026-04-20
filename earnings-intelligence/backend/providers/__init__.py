from .price_provider import YahooPriceProvider
from .filings_provider import EdgarFilingsProvider
from .news_provider import NewsApiProvider
from .ratings_provider import YahooRatingsProvider
from config import settings


def get_price_provider():
    return YahooPriceProvider()


def get_filings_provider():
    return EdgarFilingsProvider()


def get_news_provider():
    return NewsApiProvider(api_key=settings.news_api_key)


def get_ratings_provider():
    return YahooRatingsProvider()
