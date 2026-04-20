from providers import get_filings_provider, get_news_provider
import yfinance as yf


def get_events_timeline(ticker: str) -> list[dict]:
    """Unified timeline of 8-K filings + news articles, sorted descending."""
    filings_prov = get_filings_provider()
    news_prov = get_news_provider()

    events = []

    # 8-K filings
    try:
        filings = filings_prov.get_8k_filings(ticker, years_back=3)
        for f in filings:
            events.append({
                "date": f.get("date", ""),
                "title": f.get("title", ""),
                "type": "8K",
                "source": "SEC EDGAR",
                "url": f.get("url", ""),
                "description": f.get("description", ""),
                "status": "pending",
            })
    except Exception:
        pass

    # News articles
    try:
        t = yf.Ticker(ticker)
        company_name = (t.info or {}).get("longName", ticker)
        articles = news_prov.get_articles(ticker, company_name, years_back=3)
        for a in articles:
            events.append({
                "date": a.get("date", ""),
                "title": a.get("title", ""),
                "type": "news",
                "source": a.get("source", ""),
                "url": a.get("url", ""),
                "description": a.get("description", ""),
                "status": "pending",
            })
    except Exception:
        pass

    # Sort descending by date
    events.sort(key=lambda x: x.get("date", ""), reverse=True)
    return events
