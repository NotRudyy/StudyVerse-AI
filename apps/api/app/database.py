from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True) if settings.database_url and not settings.demo_mode else None
SessionLocal = async_sessionmaker(engine, expire_on_commit=False) if engine else None


async def get_session() -> AsyncIterator[AsyncSession | None]:
    if SessionLocal is None:
        yield None
        return
    async with SessionLocal() as session:
        yield session
