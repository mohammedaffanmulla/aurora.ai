from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from aurora.database.engine import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session