from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . config import settings

SQLAPCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.database_username}\
:{settings.database_password}@{settings.database_hostname}:\
    {settings.database_port}/{settings.database_name}"

Base = declarative_base()

engine = create_async_engine(
    SQLAPCHEMY_DATABASE_URL, 
    future=True,
    )

Async_Session = sessionmaker(engine, class_=AsyncSession,
                             expire_on_commit=False,
                             autoflush=False)


async def get_db():
    try:
        session: AsyncSession = Async_Session()
        yield session
    finally:
        await session.close()