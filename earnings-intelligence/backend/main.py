import asyncio
import io
import json
import zipfile
from datetime import datetime
from typing import Optional

import pdfplumber
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from config import settings
from modules.ai_synthesis import stream_ai_synthesis
from modules.earnings_summary import get_earnings_summary
from modules.events_timeline import get_events_timeline
from modules.guidance_tracker import get_guidance_tracker
from modules.price_performance import get_price_performance
from pdf_export.exporter import generate_pdf
from research_store.store import (
    get_approved_events,
    get_research_doc_texts,
    get_research_docs,
    init_db,
    save_event_item,
    save_research_doc,
    update_event_status,
)

app = FastAPI(title="Earnings Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ── Full report ──────────────────────────────────────────────────────────────

@app.get("/api/report/{ticker}")
async def get_report(ticker: str, period: str = "Q4 2024"):
    ticker = ticker.upper()

    earnings, events, guidance, price = await asyncio.gather(
        asyncio.to_thread(get_earnings_summary, ticker, period),
        asyncio.to_thread(get_events_timeline, ticker),
        asyncio.to_thread(get_guidance_tracker, ticker),
        asyncio.to_thread(get_price_performance, ticker),
    )

    return {
        "ticker": ticker,
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "earnings_summary": earnings,
        "events_timeline": events[:50],
        "guidance_tracker": guidance,
        "price_performance": price,
    }


# ── AI synthesis SSE stream ──────────────────────────────────────────────────

@app.get("/api/report/{ticker}/stream")
async def stream_report(ticker: str, period: str = "Q4 2024"):
    ticker = ticker.upper()

    earnings, events, guidance, price = await asyncio.gather(
        asyncio.to_thread(get_earnings_summary, ticker, period),
        asyncio.to_thread(get_events_timeline, ticker),
        asyncio.to_thread(get_guidance_tracker, ticker),
        asyncio.to_thread(get_price_performance, ticker),
    )

    research_docs = await get_research_doc_texts(ticker)

    async def event_generator():
        try:
            async for chunk in stream_ai_synthesis(
                ticker=ticker,
                period=period,
                earnings_summary=earnings,
                events=events,
                guidance=guidance,
                price_performance=price,
                research_docs=research_docs,
            ):
                data = json.dumps({"chunk": chunk})
                yield f"data: {data}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Individual module endpoints ───────────────────────────────────────────────

@app.get("/api/price/{ticker}")
async def get_price(ticker: str):
    ticker = ticker.upper()
    return await asyncio.to_thread(get_price_performance, ticker)


@app.get("/api/filings/{ticker}")
async def get_filings(ticker: str):
    from providers import get_filings_provider
    ticker = ticker.upper()
    provider = get_filings_provider()
    filings = await asyncio.to_thread(provider.get_8k_filings, ticker, 3)
    return {"ticker": ticker, "filings": filings}


@app.get("/api/events/{ticker}")
async def get_events(ticker: str):
    ticker = ticker.upper()
    events = await asyncio.to_thread(get_events_timeline, ticker)
    approved = await get_approved_events(ticker)
    approved_urls = {e["url"] for e in approved}
    for e in events:
        if e["url"] in approved_urls:
            e["status"] = "approved"
    return {"ticker": ticker, "events": events}


@app.post("/api/events/{ticker}/approve")
async def approve_event(ticker: str, body: dict):
    ticker = ticker.upper()
    event = body.get("event", {})
    if not event:
        raise HTTPException(status_code=400, detail="event payload required")
    status = body.get("status", "approved")
    event_id = await save_event_item(ticker, {**event, "status": status})
    return {"id": event_id, "status": status}


@app.get("/api/ratings/{ticker}")
async def get_ratings(ticker: str):
    from providers import get_ratings_provider
    ticker = ticker.upper()
    provider = get_ratings_provider()
    changes = await asyncio.to_thread(provider.get_rating_changes, ticker)
    consensus = await asyncio.to_thread(provider.get_consensus, ticker)
    return {"ticker": ticker, "changes": changes, "consensus": consensus}


# ── Research store endpoints ─────────────────────────────────────────────────

@app.post("/api/research/upload")
async def upload_research(
    ticker: str = Form(...),
    file: UploadFile = File(...),
):
    ticker = ticker.upper()
    contents = await file.read()
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF parse error: {e}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    doc_id = await save_research_doc(ticker, file.filename or "upload.pdf", text)
    return {"id": doc_id, "ticker": ticker, "filename": file.filename, "chars": len(text)}


@app.get("/api/research/{ticker}")
async def list_research(ticker: str):
    ticker = ticker.upper()
    docs = await get_research_docs(ticker)
    return {"ticker": ticker, "docs": docs}


# ── PDF export ───────────────────────────────────────────────────────────────

@app.get("/api/report/{ticker}/pdf")
async def get_report_pdf(ticker: str, period: str = "Q4 2024"):
    ticker = ticker.upper()

    earnings, events, guidance, price = await asyncio.gather(
        asyncio.to_thread(get_earnings_summary, ticker, period),
        asyncio.to_thread(get_events_timeline, ticker),
        asyncio.to_thread(get_guidance_tracker, ticker),
        asyncio.to_thread(get_price_performance, ticker),
    )

    report_data = {
        "ticker": ticker,
        "period": period,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "earnings": earnings,
        "events": events[:50],
        "guidance": guidance,
        "price": price,
        "synthesis": None,
    }

    pdf_bytes = await asyncio.to_thread(generate_pdf, report_data)
    filename = f"{ticker}_{period.replace(' ', '_')}_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Batch mode ────────────────────────────────────────────────────────────────

class BatchRequest(BaseModel):
    tickers: list[str]
    period: str = "Q4 2024"


@app.post("/api/batch")
async def batch_report(body: BatchRequest):
    period = body.period

    async def process_ticker(ticker: str) -> tuple[str, dict, bytes]:
        ticker = ticker.upper()
        earnings, events, guidance, price = await asyncio.gather(
            asyncio.to_thread(get_earnings_summary, ticker, period),
            asyncio.to_thread(get_events_timeline, ticker),
            asyncio.to_thread(get_guidance_tracker, ticker),
            asyncio.to_thread(get_price_performance, ticker),
        )
        report_data = {
            "ticker": ticker,
            "period": period,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "earnings": earnings,
            "events": events[:50],
            "guidance": guidance,
            "price": price,
            "synthesis": None,
        }
        pdf_bytes = await asyncio.to_thread(generate_pdf, report_data)
        combined_json = {
            "ticker": ticker,
            "period": period,
            "earnings_summary": earnings,
            "events_timeline": events[:50],
            "guidance_tracker": guidance,
            "price_performance": price,
        }
        return ticker, combined_json, pdf_bytes

    results = await asyncio.gather(*[process_ticker(t) for t in body.tickers])

    # Build zip in memory
    buf = io.BytesIO()
    all_json = []
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for ticker, combined_json, pdf_bytes in results:
            zf.writestr(f"{ticker}_{period.replace(' ', '_')}.pdf", pdf_bytes)
            all_json.append(combined_json)
        zf.writestr("batch_summary.json", json.dumps(all_json, indent=2, default=str))

    buf.seek(0)
    filename = f"batch_{period.replace(' ', '_')}.zip"
    return Response(
        content=buf.read(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
