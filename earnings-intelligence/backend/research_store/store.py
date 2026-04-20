from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from .models import Base, ResearchDoc, EventItem
from config import settings


engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_research_doc(ticker: str, filename: str, text_content: str) -> int:
    async with AsyncSessionLocal() as session:
        doc = ResearchDoc(ticker=ticker.upper(), filename=filename, text_content=text_content)
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc.id


async def get_research_docs(ticker: str) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ResearchDoc)
            .where(ResearchDoc.ticker == ticker.upper())
            .order_by(ResearchDoc.upload_date.desc())
        )
        docs = result.scalars().all()
        return [
            {
                "id": d.id,
                "ticker": d.ticker,
                "filename": d.filename,
                "upload_date": d.upload_date.isoformat() if d.upload_date else None,
                "text_snippet": d.text_content[:500],
            }
            for d in docs
        ]


async def get_research_doc_texts(ticker: str, limit: int = 3) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ResearchDoc)
            .where(ResearchDoc.ticker == ticker.upper())
            .order_by(ResearchDoc.upload_date.desc())
            .limit(limit)
        )
        docs = result.scalars().all()
        return [{"filename": d.filename, "text": d.text_content} for d in docs]


async def save_event_item(ticker: str, event: dict) -> int:
    async with AsyncSessionLocal() as session:
        item = EventItem(
            ticker=ticker.upper(),
            date=event.get("date", ""),
            title=event.get("title", ""),
            event_type=event.get("type", ""),
            source=event.get("source", ""),
            url=event.get("url", ""),
            description=event.get("description", ""),
            status=event.get("status", "pending"),
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item.id


async def update_event_status(event_id: int, status: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(EventItem).where(EventItem.id == event_id))
        item = result.scalar_one_or_none()
        if item:
            item.status = status
            await session.commit()


async def get_approved_events(ticker: str) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(EventItem)
            .where(EventItem.ticker == ticker.upper(), EventItem.status == "approved")
            .order_by(EventItem.date.desc())
        )
        items = result.scalars().all()
        return [
            {
                "id": i.id,
                "date": i.date,
                "title": i.title,
                "type": i.event_type,
                "source": i.source,
                "url": i.url,
                "description": i.description,
                "status": i.status,
            }
            for i in items
        ]
