import yfinance as yf
import pandas as pd
from providers.mock_data import MOCK_EARNINGS_HISTORY


def _safe_float(v):
    try:
        return float(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else None
    except Exception:
        return None


def _guidance_style(beat_rate: float, avg_beat: float) -> str:
    if beat_rate >= 0.75 and avg_beat > 3:
        return "conservative"
    if beat_rate <= 0.40 or avg_beat < -2:
        return "aggressive"
    return "in-line"


def _mock_guidance(ticker: str) -> dict:
    quarters = []
    beat_count = 0
    beat_magnitudes = []
    for entry in MOCK_EARNINGS_HISTORY:
        quarters.append({
            "date": entry["date"],
            "eps_actual": entry["eps_actual"],
            "eps_estimate": entry["eps_estimate"],
            "eps_beat_pct": entry["beat_pct"],
            "beat": entry["beat_pct"] > 0,
            "revenue_actual": None,
            "revenue_guided_low": None,
            "revenue_guided_high": None,
        })
        if entry["beat_pct"] > 0:
            beat_count += 1
        beat_magnitudes.append(entry["beat_pct"])

    n = len(quarters)
    beat_rate = beat_count / n if n else None
    avg_beat = sum(beat_magnitudes) / len(beat_magnitudes) if beat_magnitudes else None
    return {
        "ticker": ticker,
        "source": "demo",
        "quarters": quarters,
        "summary": {
            "quarters_analyzed": n,
            "beat_count": beat_count,
            "beat_rate": round(beat_rate * 100, 1) if beat_rate is not None else None,
            "avg_beat_magnitude_pct": round(avg_beat, 2) if avg_beat is not None else None,
            "guidance_style": _guidance_style(beat_rate or 0, avg_beat or 0),
        },
    }


def get_guidance_tracker(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        quarters = []
        beat_count = 0
        beat_magnitudes = []

        eh = t.earnings_history
        if eh is None or eh.empty:
            return _mock_guidance(ticker)

        eh = eh.reset_index()
        recent = eh.head(6)
        for _, row in recent.iterrows():
            actual = _safe_float(row.get("EPS Actual") or row.get("Reported EPS"))
            estimate = _safe_float(row.get("EPS Estimate"))
            date_str = str(row.get("Earnings Date") or row.get("Quarter") or "")[:10]

            beat_pct = None
            if actual is not None and estimate is not None and estimate != 0:
                beat_pct = round((actual - estimate) / abs(estimate) * 100, 2)
                if beat_pct > 0:
                    beat_count += 1
                beat_magnitudes.append(beat_pct)

            quarters.append({
                "date": date_str,
                "eps_actual": actual,
                "eps_estimate": estimate,
                "eps_beat_pct": beat_pct,
                "beat": beat_pct > 0 if beat_pct is not None else None,
                "revenue_actual": None,
                "revenue_guided_low": None,
                "revenue_guided_high": None,
            })

        if not quarters:
            return _mock_guidance(ticker)

        n = len(quarters)
        beat_rate = beat_count / n if n > 0 else None
        avg_beat = sum(beat_magnitudes) / len(beat_magnitudes) if beat_magnitudes else None
        return {
            "ticker": ticker,
            "quarters": quarters,
            "summary": {
                "quarters_analyzed": n,
                "beat_count": beat_count,
                "beat_rate": round(beat_rate * 100, 1) if beat_rate is not None else None,
                "avg_beat_magnitude_pct": round(avg_beat, 2) if avg_beat is not None else None,
                "guidance_style": _guidance_style(beat_rate or 0, avg_beat or 0) if beat_rate is not None else "unknown",
            },
        }
    except Exception:
        return _mock_guidance(ticker)
