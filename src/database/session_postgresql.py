from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from config import get_settings

settings = get_settings()

POSTGRESQL_DATABASE_URL = (f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
                           f"{settings.POSTGRES_HOST}:{settings.POSTGRES_DB_PORT}/{settings.POSTGRES_DB}")
postgresql_engine = create_async_engine(POSTGRESQL_DATABASE_URL, echo=False)

sync_database_url = POSTGRESQL_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
sync_postgresql_engine = create_engine(sync_database_url, echo=False)

AsyncPostgresqlSessionLocal = sessionmaker(  # type: ignore
    bind=postgresql_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

SyncPostgresqlSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_postgresql_engine
)


async def get_postgresql_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session.

    This function returns an async generator yielding a new database session.
    It ensures that the session is properly closed after use.

    :return: An asynchronous generator yielding an AsyncSession instance.
    """
    async with AsyncPostgresqlSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_postgresql_db_contextmanager() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session using a context manager.

    This function allows for managing the database session within a `with` statement.
    It ensures that the session is properly initialized and closed after execution.

    :return: An asynchronous generator yielding an AsyncSession instance.
    """
    async with AsyncPostgresqlSessionLocal() as session:
        yield session


def get_sync_postgresql_db() -> Generator[Session, None, None]:
    """
    Provide a synchronous database session.

    This function returns a synchronous database session.
    """
    with SyncPostgresqlSessionLocal() as session:
        yield session


@contextmanager
def get_sync_postgresql_db_contextmanager() -> Generator[Session, None, None]:
    """
    Provide a synchronous database session using a context manager.

    This function allows for managing the database session within a `with` statement.

    :return: A synchronous database session.
    """
    with SyncPostgresqlSessionLocal() as session:
        yield session
