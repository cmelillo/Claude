import yfinance as yf
from providers import get_price_provider, get_ratings_provider
from config import SECTOR_ETF_MAP


def _normalize(history: list[dict]) -> list[dict]:
    """Normalize price series to 100 at start."""
    if not history:
        return []
    base = history[0]["close"]
    if not base:
        return history
    return [{**h, "normalized": round(h["close"] / base * 100, 4)} for h in history]


def get_price_performance(ticker: str) -> dict:
    price_prov = get_price_provider()
    ratings_prov = get_ratings_provider()

    info = price_prov.get_current_info(ticker)
    sector = info.get("sector", "Technology")
    etf_ticker = SECTOR_ETF_MAP.get(sector, "XLK")

    # 90-day price history
    stock_hist = price_prov.get_price_history(ticker, "90d")
    etf_hist = price_prov.get_price_history(etf_ticker, "90d")

    stock_normalized = _normalize(stock_hist.get("history", []))
    etf_normalized = _normalize(etf_hist.get("history", []))

    # Post-earnings reactions for recent earnings dates
    t = yf.Ticker(ticker)
    earnings_reactions = []
    try:
        dates = t.earnings_dates
        if dates is not None and not dates.empty:
            recent = dates.head(4).reset_index()
            for _, row in recent.iterrows():
                ed_val = row.get("Earnings Date") or row.index
                ed_str = str(ed_val)[:10]
                reaction = price_prov.get_post_earnings_reaction(ticker, ed_str)
                earnings_reactions.append(reaction)
    except Exception:
        pass

    rating_changes = ratings_prov.get_rating_changes(ticker)
    consensus = ratings_prov.get_consensus(ticker)

    return {
        "ticker": ticker,
        "sector": sector,
        "sector_etf": etf_ticker,
        "current_info": info,
        "price_chart": {
            "stock": stock_normalized,
            "etf": etf_normalized,
        },
        "earnings_reactions": earnings_reactions,
        "ratings": {
            "changes": rating_changes[:30],
            "consensus": consensus,
        },
    }
