import yfinance as yf
import pandas as pd
from datetime import datetime
from providers.mock_data import MOCK_EARNINGS_HISTORY


def _badge(actual, estimate):
    if actual is None or estimate is None or estimate == 0:
        return "N/A"
    pct = (actual - estimate) / abs(estimate) * 100
    if pct > 2:
        return "Beat"
    if pct < -2:
        return "Miss"
    return "In Line"


def _safe_float(v):
    try:
        return float(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else None
    except Exception:
        return None


def _mock_summary(ticker: str, period: str) -> dict:
    parts = period.upper().split()
    year = int(parts[1]) if len(parts) > 1 else datetime.today().year
    entry = next((e for e in MOCK_EARNINGS_HISTORY if str(year) in e["date"]), MOCK_EARNINGS_HISTORY[0])
    eps_actual = entry["eps_actual"]
    eps_estimate = entry["eps_estimate"]
    eps_surprise = entry["beat_pct"]
    return {
        "ticker": ticker,
        "period": period,
        "source": "demo",
        "eps": {
            "actual": eps_actual,
            "estimate": eps_estimate,
            "surprise_pct": eps_surprise,
            "badge": _badge(eps_actual, eps_estimate),
        },
        "revenue": {
            "actual": 35_082_000_000,
            "estimate": 33_200_000_000,
            "yoy_pct": 94.0,
            "qoq_pct": 17.2,
        },
        "margins": {
            "gross_margin_pct": 74.6,
            "operating_margin_pct": 61.1,
        },
        "guidance": {
            "next_quarter_revenue_low": 36_500_000_000,
            "next_quarter_revenue_high": 38_500_000_000,
            "next_quarter_eps_low": None,
            "next_quarter_eps_high": None,
            "source": "demo",
        },
    }


def get_earnings_summary(ticker: str, period: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        parts = period.upper().split()
        year = int(parts[1]) if len(parts) > 1 else datetime.today().year

        eps_actual = None
        eps_estimate = None
        eps_surprise_pct = None

        eh = t.earnings_history
        if eh is not None and not eh.empty:
            eh = eh.reset_index()
            for _, row in eh.iterrows():
                date_str = str(row.get("Earnings Date") or row.get("Quarter") or "")
                if str(year) in date_str:
                    actual = _safe_float(row.get("EPS Actual") or row.get("Reported EPS"))
                    estimate = _safe_float(row.get("EPS Estimate"))
                    if actual is not None:
                        eps_actual = actual
                        eps_estimate = estimate
                        if estimate and estimate != 0:
                            eps_surprise_pct = round((actual - estimate) / abs(estimate) * 100, 2)
                        break

        rev_actual = None
        rev_estimate = None
        gross_margin = None
        op_margin = None
        rev_yoy = None
        rev_qoq = None

        qf = t.quarterly_financials
        if qf is not None and not qf.empty:
            col = qf.columns[0]
            rev = _safe_float(qf.loc["Total Revenue", col]) if "Total Revenue" in qf.index else None
            cogs = _safe_float(qf.loc["Cost Of Revenue", col]) if "Cost Of Revenue" in qf.index else None
            op_inc = _safe_float(qf.loc["Operating Income", col]) if "Operating Income" in qf.index else None
            if rev:
                rev_actual = rev
                if cogs:
                    gross_margin = round((rev - cogs) / rev * 100, 2)
                if op_inc:
                    op_margin = round(op_inc / rev * 100, 2)
            if len(qf.columns) > 1:
                prev_rev = _safe_float(qf.loc["Total Revenue", qf.columns[1]]) if "Total Revenue" in qf.index else None
                if rev and prev_rev:
                    rev_qoq = round((rev - prev_rev) / abs(prev_rev) * 100, 2)
            if len(qf.columns) > 3:
                yoy_rev = _safe_float(qf.loc["Total Revenue", qf.columns[3]]) if "Total Revenue" in qf.index else None
                if rev and yoy_rev:
                    rev_yoy = round((rev - yoy_rev) / abs(yoy_rev) * 100, 2)

        if eps_actual is None and rev_actual is None:
            return _mock_summary(ticker, period)

        return {
            "ticker": ticker,
            "period": period,
            "eps": {
                "actual": eps_actual,
                "estimate": eps_estimate,
                "surprise_pct": eps_surprise_pct,
                "badge": _badge(eps_actual, eps_estimate),
            },
            "revenue": {
                "actual": rev_actual,
                "estimate": rev_estimate,
                "yoy_pct": rev_yoy,
                "qoq_pct": rev_qoq,
            },
            "margins": {
                "gross_margin_pct": gross_margin,
                "operating_margin_pct": op_margin,
            },
            "guidance": {
                "next_quarter_revenue_low": None,
                "next_quarter_revenue_high": None,
                "next_quarter_eps_low": None,
                "next_quarter_eps_high": None,
                "source": "8-K parsing not yet available",
            },
        }
    except Exception:
        return _mock_summary(ticker, period)
