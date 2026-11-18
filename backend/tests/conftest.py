"""
Pytest configuration and fixtures.
Ensures tables are initialized before running tests.
"""

import pytest
from app.db.session import init_db


@pytest.fixture(autouse=True, scope="session")
async def setup_database():
    """Ensure database tables exist for test suite."""
    await init_db()
