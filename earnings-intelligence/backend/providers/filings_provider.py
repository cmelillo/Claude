import requests
from datetime import datetime, timedelta
from .base import FilingsProvider
from . import mock_data

EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_HEADERS = {"User-Agent": "EarningsIntelligence research@example.com"}


class EdgarFilingsProvider(FilingsProvider):
    def get_8k_filings(self, ticker: str, years_back: int = 3) -> list[dict]:
        try:
            today = datetime.today()
            start = (today - timedelta(days=365 * years_back)).strftime("%Y-%m-%d")
            end = today.strftime("%Y-%m-%d")

            params = {
                "q": f'"{ticker}"',
                "dateRange": "custom",
                "startdt": start,
                "enddt": end,
                "forms": "8-K",
            }

            filings = []
            from_ = 0
            while True:
                params["from"] = from_
                resp = requests.get(
                    EDGAR_SEARCH_URL,
                    params=params,
                    headers=EDGAR_HEADERS,
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])
                if not hits:
                    break

                for hit in hits:
                    src = hit.get("_source", {})
                    filings.append({
                        "title": src.get("display_names", ticker) or src.get("entity_name", ticker),
                        "form": src.get("form_type", "8-K"),
                        "date": src.get("file_date", ""),
                        "period": src.get("period_of_report", ""),
                        "accession": src.get("accession_no", ""),
                        "url": f"https://www.sec.gov/Archives/edgar/data/{src.get('entity_id','')}/{src.get('accession_no','').replace('-','')}",
                        "description": src.get("biz_location", ""),
                    })

                total = data.get("hits", {}).get("total", {}).get("value", 0)
                from_ += len(hits)
                if from_ >= total or from_ >= 200:
                    break

            return filings
        except Exception:
            return [{**f, "source": "demo"} for f in mock_data.MOCK_FILINGS]

    def get_filing_text(self, url: str) -> str:
        try:
            resp = requests.get(url, headers=EDGAR_HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text[:50000]
        except Exception:
            return "Filing text unavailable (network restricted in demo mode)."

    def search_filings_full_text(self, ticker: str, item_type: str = "2.02") -> list[dict]:
        try:
            today = datetime.today()
            start = (today - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
            params = {
                "q": f'"{ticker}" "Item {item_type}"',
                "dateRange": "custom",
                "startdt": start,
                "enddt": today.strftime("%Y-%m-%d"),
                "forms": "8-K",
            }
            resp = requests.get(EDGAR_SEARCH_URL, params=params, headers=EDGAR_HEADERS, timeout=15)
            resp.raise_for_status()
            hits = resp.json().get("hits", {}).get("hits", [])
            results = []
            for hit in hits:
                src = hit.get("_source", {})
                results.append({
                    "date": src.get("file_date", ""),
                    "accession": src.get("accession_no", ""),
                    "url": "",
                })
            return results
        except Exception:
            return []
