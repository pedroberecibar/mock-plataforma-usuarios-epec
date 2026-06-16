"""
conftest.py — Shared pytest fixtures for the entire test suite.

Fixtures defined here are automatically available to all test files
without needing to import them explicitly.
"""


# ---------------------------------------------------------------------------
# Markers registration (avoids PytestUnknownMarkWarning)
# ---------------------------------------------------------------------------
# Markers are also declared in pyproject.toml [tool.pytest.ini_options].
# This file documents them with examples for discoverability.

# @pytest.mark.unit        → pure unit tests, no I/O
# @pytest.mark.integration → tests that touch DB or external services
# @pytest.mark.slow        → tests that take more than 1 second


# ---------------------------------------------------------------------------
# Example shared fixtures (uncomment and adapt as needed)
# ---------------------------------------------------------------------------

# @pytest.fixture(scope="session")
# def db_engine():
#     """Create a test database engine (SQLite in-memory for unit tests)."""
#     from sqlalchemy import create_engine
#     engine = create_engine("sqlite:///:memory:", echo=False)
#     yield engine
#     engine.dispose()


# @pytest.fixture(scope="function")
# def db_session(db_engine):
#     """Provide a transactional test session that rolls back after each test."""
#     from sqlalchemy.orm import sessionmaker
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
#     yield session
#     session.rollback()
#     session.close()


# @pytest.fixture
# def anyio_backend():
#     """Use asyncio backend for async tests (requires anyio)."""
#     return "asyncio"
