import yfinance as yf
import pandas as pd
from .base import RatingsProvider
from . import mock_data


def _safe_float(v):
    try:
        return float(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else None
    except Exception:
        return None


class YahooRatingsProvider(RatingsProvider):
    def get_rating_changes(self, ticker: str) -> list[dict]:
        try:
            t = yf.Ticker(ticker)
            upgrades = t.upgrades_downgrades
            if upgrades is None or upgrades.empty:
                raise ValueError("no upgrades data")

            results = []
            upgrades = upgrades.reset_index()
            for _, row in upgrades.iterrows():
                date = row.get("GradeDate")
                if hasattr(date, "strftime"):
                    date = date.strftime("%Y-%m-%d")
                else:
                    date = str(date)[:10]
                results.append({
                    "firm": row.get("Firm", ""),
                    "from_grade": row.get("FromGrade", ""),
                    "to_grade": row.get("ToGrade", ""),
                    "action": row.get("Action", ""),
                    "date": date,
                    "price_target": None,
                })
            return sorted(results, key=lambda x: x["date"], reverse=True)
        except Exception:
            data = mock_data.MOCK_RATING_CHANGES if ticker in ("NVDA",) else []
            return [{**r, "source": "demo"} for r in data]

    def get_consensus(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            if not info:
                raise ValueError("no info")

            counts = {"buy": 0, "hold": 0, "sell": 0}
            try:
                recs = t.recommendations
                if recs is not None and not recs.empty:
                    latest = recs.iloc[-1]
                    counts["buy"] = int(latest.get("strongBuy", 0)) + int(latest.get("buy", 0))
                    counts["hold"] = int(latest.get("hold", 0))
                    counts["sell"] = int(latest.get("sell", 0)) + int(latest.get("strongSell", 0))
            except Exception:
                pass

            mean_pt = _safe_float(info.get("targetMeanPrice"))
            current = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
            pt_upside = None
            if mean_pt and current:
                pt_upside = round((mean_pt / current - 1) * 100, 1)

            return {
                "buy": counts["buy"],
                "hold": counts["hold"],
                "sell": counts["sell"],
                "mean_price_target": mean_pt,
                "current_price": current,
                "pt_upside_pct": pt_upside,
                "recommendation": info.get("recommendationKey", ""),
            }
        except Exception:
            if ticker == "NVDA":
                return {**mock_data.MOCK_CONSENSUS, "source": "demo"}
            return {
                "buy": 0, "hold": 0, "sell": 0,
                "mean_price_target": None,
                "current_price": None,
                "pt_upside_pct": None,
                "recommendation": "",
                "source": "demo",
            }
