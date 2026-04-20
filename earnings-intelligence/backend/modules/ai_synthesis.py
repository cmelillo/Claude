import json
import anthropic
from typing import AsyncGenerator
from config import settings

SYSTEM_PROMPT = """You are a senior equity research analyst assistant. Given structured \
earnings data, a contextual events timeline, management guidance history, \
and price/analyst data, write a synthesis of what this quarter means in \
the context of the company's recent history. Cover: (1) what the print \
reveals about business momentum, (2) how it relates to the key events \
of the past 2-3 years, (3) management credibility based on guidance \
accuracy, (4) what the analyst community is signaling, (5) key risks \
and bull/bear considerations. Be direct, specific, and avoid filler. \
Write for a professional investor."""


async def stream_ai_synthesis(
    ticker: str,
    period: str,
    earnings_summary: dict,
    events: list[dict],
    guidance: dict,
    price_performance: dict,
    research_docs: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    payload = {
        "ticker": ticker,
        "period": period,
        "earnings_summary": earnings_summary,
        "events_timeline": events[:30],
        "guidance_tracker": guidance,
        "price_performance": {
            k: v for k, v in price_performance.items() if k != "price_chart"
        },
    }

    if research_docs:
        payload["uploaded_research"] = research_docs[:3]

    user_message = f"""Please analyze the following structured earnings intelligence data for {ticker} ({period}):

```json
{json.dumps(payload, indent=2, default=str)}
```

Write your synthesis now."""

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
