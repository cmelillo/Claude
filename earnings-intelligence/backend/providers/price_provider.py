import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .base import PriceProvider
from . import mock_data


def _safe_float(v):
    try:
        return float(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else None
    except Exception:
        return None


class YahooPriceProvider(PriceProvider):
    def get_price_history(self, ticker: str, period: str = "1y") -> dict:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period)
            if hist.empty:
                raise ValueError("empty history")
            records = []
            for date, row in hist.iterrows():
                records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 4),
                    "high": round(float(row["High"]), 4),
                    "low": round(float(row["Low"]), 4),
                    "close": round(float(row["Close"]), 4),
                    "volume": int(row["Volume"]),
                })
            return {"ticker": ticker, "history": records}
        except Exception:
            cached = mock_data.MOCK_PRICE_HISTORY.get(ticker, mock_data._price_series(ticker))
            return {"ticker": ticker, "history": cached, "source": "demo"}

    def get_current_info(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            if not info.get("longName"):
                raise ValueError("no info returned")
            return {
                "ticker": ticker,
                "company_name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "current_price": _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "week_52_high": _safe_float(info.get("fiftyTwoWeekHigh")),
                "week_52_low": _safe_float(info.get("fiftyTwoWeekLow")),
                "pe_ratio": _safe_float(info.get("trailingPE")),
                "forward_pe": _safe_float(info.get("forwardPE")),
            }
        except Exception:
            return mock_data.MOCK_INFO.get(ticker, {
                "ticker": ticker,
                "company_name": ticker,
                "sector": "Technology",
                "industry": "Unknown",
                "current_price": None,
                "market_cap": None,
                "shares_outstanding": None,
                "week_52_high": None,
                "week_52_low": None,
                "pe_ratio": None,
                "forward_pe": None,
                "source": "demo",
            })

    def get_post_earnings_reaction(self, ticker: str, earnings_date: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            ed = datetime.strptime(earnings_date, "%Y-%m-%d")
            start = (ed - timedelta(days=3)).strftime("%Y-%m-%d")
            end = (ed + timedelta(days=30)).strftime("%Y-%m-%d")
            hist = t.history(start=start, end=end)
            if hist.empty:
                raise ValueError("empty")

            dates = hist.index.tolist()
            ed_ts = pd.Timestamp(earnings_date)
            future = [d for d in dates if d >= ed_ts]
            prior = [d for d in dates if d < ed_ts]
            if not future or not prior:
                raise ValueError("no data")

            prior_close = float(hist.loc[prior[-1], "Close"])

            def ret(idx):
                if idx < len(future):
                    return round((float(hist.loc[future[idx], "Close"]) / prior_close - 1) * 100, 2)
                return None

            return {
                "earnings_date": earnings_date,
                "prior_close": round(prior_close, 4),
                "t1": ret(0),
                "t5": ret(4),
                "t22": ret(21),
            }
        except Exception:
            # Return mock reaction for the closest known earnings date
            for r in mock_data.MOCK_EARNINGS_REACTIONS:
                if r["earnings_date"] == earnings_date:
                    return {**r, "source": "demo"}
            if mock_data.MOCK_EARNINGS_REACTIONS:
                return {**mock_data.MOCK_EARNINGS_REACTIONS[0], "earnings_date": earnings_date, "source": "demo"}
            return {"earnings_date": earnings_date, "t1": None, "t5": None, "t22": None}

    def get_sector_etf_history(self, etf_ticker: str, period: str = "90d") -> dict:
        return self.get_price_history(etf_ticker, period)
