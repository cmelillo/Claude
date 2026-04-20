# Earnings Intelligence — Project Memory

## What this is
A full-stack earnings research tool for fundamental equity analysts. Given a ticker + earnings period, it assembles a 5-module structured report: earnings summary, events timeline, guidance tracker, price performance, and AI synthesis.

## Quick start

### Backend (FastAPI)
```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate      # Windows: ..\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in API keys
uvicorn main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev                      # starts on http://localhost:3000
```

The Vite dev server proxies `/api/*` to `http://127.0.0.1:8000`.

## Environment variables (backend/.env)
| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Powers Module 5 AI synthesis |
| `NEWS_API_KEY` | Optional | NewsAPI free key for news events |
| `SECRET_KEY` | Yes | Session signing key |
| `DATABASE_URL` | No | Defaults to SQLite in project dir |

## Project structure
```
earnings-intelligence/
├── backend/
│   ├── main.py                  # FastAPI app, all endpoints
│   ├── config.py                # Settings, PROVIDER_MAP, SECTOR_ETF_MAP
│   ├── providers/               # All data connectors
│   │   ├── base.py              # Abstract base classes (PriceProvider, etc.)
│   │   ├── price_provider.py    # YahooPriceProvider (falls back to mock)
│   │   ├── filings_provider.py  # EdgarFilingsProvider (falls back to mock)
│   │   ├── news_provider.py     # NewsApiProvider (falls back to mock)
│   │   ├── ratings_provider.py  # YahooRatingsProvider (falls back to mock)
│   │   ├── mock_data.py         # Demo data for NVDA (used in network-restricted envs)
│   │   └── __init__.py          # Factory functions: get_price_provider(), etc.
│   ├── modules/                 # Business logic, provider-agnostic
│   │   ├── earnings_summary.py  # Module 1
│   │   ├── events_timeline.py   # Module 2
│   │   ├── guidance_tracker.py  # Module 3
│   │   ├── price_performance.py # Module 4
│   │   └── ai_synthesis.py      # Module 5 (SSE streaming)
│   ├── research_store/
│   │   ├── models.py            # SQLAlchemy models (ResearchDoc, EventItem)
│   │   └── store.py             # Async CRUD helpers
│   └── pdf_export/
│       ├── exporter.py          # WeasyPrint PDF generator
│       └── report_template.html # Jinja2 HTML template for PDF
└── frontend/
    └── src/
        ├── App.jsx              # Root component, orchestrates modules
        ├── components/          # One component per module
        └── api/client.js        # All fetch + EventSource calls
```

## API endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/report/{ticker}?period=Q4+2024` | Full 5-module report JSON |
| GET | `/api/report/{ticker}/stream?period=…` | SSE stream for AI synthesis |
| GET | `/api/report/{ticker}/pdf?period=…` | Download PDF report |
| GET | `/api/price/{ticker}` | Price + ratings data |
| GET | `/api/filings/{ticker}` | SEC 8-K filing list |
| GET | `/api/events/{ticker}` | Unified events timeline |
| GET | `/api/ratings/{ticker}` | Analyst ratings + consensus |
| POST | `/api/events/{ticker}/approve` | Approve/dismiss an event |
| POST | `/api/research/upload` | Upload analyst PDF |
| GET | `/api/research/{ticker}` | List uploaded docs |
| POST | `/api/batch` | Batch multi-ticker report + zip |

## Provider abstraction pattern

Every provider inherits from an abstract base in `providers/base.py`:

```python
# providers/base.py
class PriceProvider(ABC):
    @abstractmethod
    def get_price_history(self, ticker: str, period: str) -> dict: ...
    
    @abstractmethod
    def get_current_info(self, ticker: str) -> dict: ...
    
    @abstractmethod
    def get_post_earnings_reaction(self, ticker: str, earnings_date: str) -> dict: ...
```

### Adding a new provider (e.g. Bloomberg)

1. Create `providers/bloomberg_price_provider.py`:
```python
from .base import PriceProvider

class BloombergPriceProvider(PriceProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_price_history(self, ticker, period):
        # Bloomberg API call here
        ...
```

2. Register it in `providers/__init__.py`:
```python
def get_price_provider():
    if settings.price_provider == "bloomberg":
        return BloombergPriceProvider(api_key=settings.bloomberg_api_key)
    return YahooPriceProvider()
```

3. Add `price_provider=bloomberg` to your `.env`.

No module code needs to change. The factory function handles dispatch.

## Module system

Each module in `modules/` is a pure function that accepts a ticker (and optionally a period) and returns a dict. Modules call providers via the factory functions in `providers/__init__.py`.

### Adding a new module

1. Create `modules/your_module.py`:
```python
from providers import get_price_provider

def get_your_data(ticker: str) -> dict:
    provider = get_price_provider()
    # ... logic
    return {"ticker": ticker, "data": ...}
```

2. Add an endpoint in `main.py`:
```python
@app.get("/api/yourmodule/{ticker}")
async def your_module(ticker: str):
    return await asyncio.to_thread(get_your_data, ticker.upper())
```

3. Add it to the main `/api/report/{ticker}` gather call.

## Batch mode
```bash
curl -X POST http://localhost:8000/api/batch \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["NVDA", "AAPL", "MSFT"], "period": "Q4 2024"}' \
  --output batch.zip
```

Returns a zip file containing one PDF per ticker plus a `batch_summary.json`.

## Demo / fallback mode

All providers catch network errors and fall back to realistic mock data (primarily for NVDA). This allows the full app to be demoed in network-restricted environments. Components show a "Demo data" banner when fallback data is active.

## Swapping data sources later

| Source | Currently | To upgrade |
|---|---|---|
| Price | yfinance (free) | Bloomberg, Refinitiv, FactSet |
| Filings | SEC EDGAR (free) | Document AI, proprietary parsing |
| News | NewsAPI free tier | Bloomberg News, Factiva |
| Ratings | yfinance (free) | Bloomberg, FactSet |

All swaps require only: new provider class + update factory in `providers/__init__.py` + new env var.
