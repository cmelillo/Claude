"""Realistic mock data for NVDA used when network providers are unavailable."""
from datetime import datetime, timedelta
import random

random.seed(42)


def _price_series(ticker: str, days: int = 90, start_price: float = 100.0):
    records = []
    price = start_price
    for i in range(days):
        date = (datetime.today() - timedelta(days=days - i)).strftime("%Y-%m-%d")
        change = random.gauss(0.001, 0.025)
        price = max(price * (1 + change), 1.0)
        records.append({
            "date": date,
            "open": round(price * random.uniform(0.98, 1.0), 4),
            "high": round(price * random.uniform(1.0, 1.02), 4),
            "low": round(price * random.uniform(0.97, 1.0), 4),
            "close": round(price, 4),
            "volume": random.randint(20_000_000, 80_000_000),
        })
    return records


MOCK_PRICE_HISTORY = {
    "NVDA": _price_series("NVDA", 365, 450.0),
    "AAPL": _price_series("AAPL", 365, 170.0),
    "MSFT": _price_series("MSFT", 365, 380.0),
}

MOCK_INFO = {
    "NVDA": {
        "ticker": "NVDA",
        "company_name": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
        "current_price": 875.40,
        "market_cap": 2_160_000_000_000,
        "shares_outstanding": 2_460_000_000,
        "week_52_high": 974.00,
        "week_52_low": 394.00,
        "pe_ratio": 65.2,
        "forward_pe": 34.8,
    },
    "AAPL": {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "current_price": 172.50,
        "market_cap": 2_660_000_000_000,
        "shares_outstanding": 15_430_000_000,
        "week_52_high": 199.62,
        "week_52_low": 164.08,
        "pe_ratio": 27.4,
        "forward_pe": 25.1,
    },
}

MOCK_EARNINGS_REACTIONS = [
    {"earnings_date": "2024-11-20", "prior_close": 141.0, "t1": 3.4, "t5": 7.2, "t22": 12.1},
    {"earnings_date": "2024-08-28", "prior_close": 125.6, "t1": 9.3, "t5": 11.4, "t22": 15.2},
    {"earnings_date": "2024-05-22", "prior_close": 87.4, "t1": 16.8, "t5": 19.3, "t22": 28.5},
]

MOCK_FILINGS = [
    {
        "title": "NVIDIA Corporation — Form 8-K (Results of Operations)",
        "form": "8-K",
        "date": "2024-11-20",
        "period": "2024-10-31",
        "accession": "0001045810-24-000123",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000123",
        "description": "Item 2.02 Results of Operations and Financial Condition",
    },
    {
        "title": "NVIDIA Corporation — Form 8-K (Results of Operations)",
        "form": "8-K",
        "date": "2024-08-28",
        "period": "2024-07-31",
        "accession": "0001045810-24-000089",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000089",
        "description": "Item 2.02 Results of Operations and Financial Condition",
    },
    {
        "title": "NVIDIA Corporation — Form 8-K (Other Events)",
        "form": "8-K",
        "date": "2024-06-10",
        "period": "2024-06-10",
        "accession": "0001045810-24-000078",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000078",
        "description": "Item 8.01 Other Events — Forward Stock Split",
    },
    {
        "title": "NVIDIA Corporation — Form 8-K (Results of Operations)",
        "form": "8-K",
        "date": "2024-05-22",
        "period": "2024-04-28",
        "accession": "0001045810-24-000055",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000055",
        "description": "Item 2.02 Results of Operations and Financial Condition",
    },
    {
        "title": "NVIDIA Corporation — Form 8-K (Results of Operations)",
        "form": "8-K",
        "date": "2024-02-21",
        "period": "2024-01-28",
        "accession": "0001045810-24-000022",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000022",
        "description": "Item 2.02 Results of Operations and Financial Condition",
    },
    {
        "title": "NVIDIA Corporation — Form 8-K (Departure/Appointment of Directors)",
        "form": "8-K",
        "date": "2023-11-21",
        "period": "2023-10-29",
        "accession": "0001045810-23-000098",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581023000098",
        "description": "Item 2.02 Results of Operations and Financial Condition",
    },
]

MOCK_NEWS = [
    {
        "title": "NVIDIA Crushes Q3 Earnings Estimates as AI Demand Surges",
        "source": "Reuters",
        "date": "2024-11-21",
        "url": "https://reuters.com/nvda-q3",
        "description": "NVIDIA reported $35.1B revenue, well above the $33.2B consensus estimate.",
        "type": "news",
    },
    {
        "title": "NVIDIA's Blackwell Architecture Ramps Ahead of Schedule",
        "source": "Bloomberg",
        "date": "2024-10-15",
        "url": "https://bloomberg.com/nvda-blackwell",
        "description": "Blackwell GPU production ramping faster than expected, raising supply concerns.",
        "type": "news",
    },
    {
        "title": "US Restricts Advanced Chip Exports to China — NVDA Among Affected",
        "source": "Wall Street Journal",
        "date": "2024-10-07",
        "url": "https://wsj.com/nvda-china",
        "description": "New export controls target advanced AI chips including NVIDIA H800.",
        "type": "industry",
    },
    {
        "title": "NVIDIA Announces 10-for-1 Stock Split",
        "source": "CNBC",
        "date": "2024-06-10",
        "url": "https://cnbc.com/nvda-split",
        "description": "NVIDIA's forward split takes effect June 10, boosting retail accessibility.",
        "type": "news",
    },
    {
        "title": "Generative AI Spending Accelerates Across Cloud Hyperscalers",
        "source": "Morgan Stanley Research",
        "date": "2024-05-01",
        "url": "https://morganstanley.com/ai-spending",
        "description": "Capex forecasts revised up 20% as Microsoft, Google, Amazon accelerate AI infrastructure.",
        "type": "industry",
    },
]

MOCK_RATING_CHANGES = [
    {"firm": "Morgan Stanley", "from_grade": "Overweight", "to_grade": "Overweight", "action": "main", "date": "2024-12-01", "price_target": 1100},
    {"firm": "Goldman Sachs", "from_grade": "Buy", "to_grade": "Buy", "action": "main", "date": "2024-11-22", "price_target": 1050},
    {"firm": "Barclays", "from_grade": "Overweight", "to_grade": "Overweight", "action": "up", "date": "2024-11-21", "price_target": 1000},
    {"firm": "Bank of America", "from_grade": "Buy", "to_grade": "Buy", "action": "main", "date": "2024-11-20", "price_target": 980},
    {"firm": "JPMorgan", "from_grade": "Overweight", "to_grade": "Overweight", "action": "main", "date": "2024-10-15", "price_target": 950},
    {"firm": "Citi", "from_grade": "Neutral", "to_grade": "Buy", "action": "up", "date": "2024-09-10", "price_target": 900},
    {"firm": "Deutsche Bank", "from_grade": "Hold", "to_grade": "Buy", "action": "up", "date": "2024-08-29", "price_target": 850},
    {"firm": "UBS", "from_grade": "Buy", "to_grade": "Buy", "action": "main", "date": "2024-08-28", "price_target": 800},
]

MOCK_CONSENSUS = {
    "buy": 38,
    "hold": 7,
    "sell": 2,
    "mean_price_target": 1025.00,
    "current_price": 875.40,
    "pt_upside_pct": 17.1,
    "recommendation": "strong_buy",
}

MOCK_EARNINGS_HISTORY = [
    {"date": "2024-11-20", "eps_actual": 0.81, "eps_estimate": 0.74, "beat_pct": 9.5},
    {"date": "2024-08-28", "eps_actual": 0.68, "eps_estimate": 0.60, "beat_pct": 13.3},
    {"date": "2024-05-22", "eps_actual": 0.61, "eps_estimate": 0.52, "beat_pct": 17.3},
    {"date": "2024-02-21", "eps_actual": 0.49, "eps_estimate": 0.37, "beat_pct": 32.4},
    {"date": "2023-11-21", "eps_actual": 0.40, "eps_estimate": 0.32, "beat_pct": 25.0},
    {"date": "2023-08-23", "eps_actual": 0.27, "eps_estimate": 0.09, "beat_pct": 200.0},
]
