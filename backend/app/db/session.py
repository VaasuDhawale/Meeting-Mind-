"""
Database session management.

Provides async SQLAlchemy engine and session factory.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Create async engine
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables and run non-destructive schema migrations."""
    from app.db.base import Base
    import app.db.models  # noqa: F401
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Check for missing columns in existing SQLite table and add them safely
        if settings.database_url.startswith("sqlite"):
            try:
                res = await conn.execute(text("PRAGMA table_info(meeting_sessions);"))
                existing_cols = {row[1] for row in res.fetchall()}
                new_columns = [
                    ("questions_answers", "JSON DEFAULT '[]'"),
                    ("timeline", "JSON DEFAULT '[]'"),
                    ("document_analysis", "JSON DEFAULT '{}'"),
                    ("evidence", "JSON DEFAULT '[]'"),
                    ("docx_path", "VARCHAR(500)"),
                ]
                for col_name, col_def in new_columns:
                    if col_name not in existing_cols:
                        await conn.execute(text(f"ALTER TABLE meeting_sessions ADD COLUMN {col_name} {col_def};"))
            except Exception:
                pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
