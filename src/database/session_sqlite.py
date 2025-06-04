from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings
from database import Base

settings = get_settings()

SQLITE_DATABASE_URL = f"sqlite+aiosqlite:///{settings.PATH_TO_DB}"
sqlite_engine = create_async_engine(SQLITE_DATABASE_URL, echo=False)
AsyncSQLiteSessionLocal = sessionmaker(  # type: ignore
    bind=sqlite_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SYNC_SQLITE_DATABASE_URL = f"sqlite:///{settings.PATH_TO_DB}"
sync_sqlite_engine = create_engine(SYNC_SQLITE_DATABASE_URL, echo=False)

SyncSQLiteSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_sqlite_engine
)


async def get_sqlite_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session.

    This function returns an async generator yielding a new database session.
    It ensures that the session is properly closed after use.

    :return: An asynchronous generator yielding an AsyncSession instance.
    """
    async with AsyncSQLiteSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_sqlite_db_contextmanager() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session using a context manager.

    This function allows for managing the database session within a `with` statement.
    It ensures that the session is properly initialized and closed after execution.

    :return: An asynchronous generator yielding an AsyncSession instance.
    """
    async with AsyncSQLiteSessionLocal() as session:
        yield session


async def reset_sqlite_database() -> None:
    """
    Reset the SQLite database.

    This function drops all existing tables and recreates them.
    It is useful for testing purposes or when resetting the database is required.

    Warning: This action is irreversible and will delete all stored data.

    :return: None
    """
    async with sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def get_sync_sqlite_db() -> Generator[Session, None, None]:
    """
    Provide a synchronous database session.

    This function returns a synchronous database session.

    :return: A synchronous database session.
    """
    with SyncSQLiteSessionLocal() as session:
        yield session


@contextmanager
def get_sync_sqlite_db_contextmanager() -> Generator[Session, None, None]:
    """
    Provide a synchronous database session using a context manager.

    This function allows for managing the database session within a `with` statement.

    :return: A synchronous database session.
    """
    with SyncSQLiteSessionLocal() as session:
        yield session
