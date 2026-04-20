import requests
from datetime import datetime, timedelta
from .base import NewsProvider
from . import mock_data

NEWS_API_BASE = "https://newsapi.org/v2/everything"


class NewsApiProvider(NewsProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_articles(self, ticker: str, company_name: str, years_back: int = 3) -> list[dict]:
        if not self.api_key:
            return [{**a, "source": "demo"} for a in mock_data.MOCK_NEWS]

        today = datetime.today()
        start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        query = f'"{ticker}" OR "{company_name}"'
        params = {
            "q": query,
            "from": start,
            "to": today.strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "pageSize": 100,
            "language": "en",
            "apiKey": self.api_key,
        }

        try:
            resp = requests.get(NEWS_API_BASE, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            articles = []
            for a in data.get("articles", []):
                pub = a.get("publishedAt", "")[:10]
                articles.append({
                    "title": a.get("title", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "date": pub,
                    "url": a.get("url", ""),
                    "description": a.get("description", ""),
                    "type": "news",
                })
            return articles
        except Exception:
            return [{**a, "source": "demo"} for a in mock_data.MOCK_NEWS]
