import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from common.types import Trend


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_pool():
    """Mock database connection pool"""
    pool = AsyncMock()
    connection = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = connection
    return pool


@pytest.fixture
def sample_trend():
    """Sample Trend object for testing"""
    return Trend(
        id="sample_id_123",
        title="Sample Trend Title",
        url="https://example.com/sample",
        source="hn",
        score=150,
        ts=datetime(2022, 1, 1, 12, 0, 0)
    )


@pytest.fixture
def sample_trends_list(sample_trend: Trend) -> list[Trend]:
    """List of sample Trend objects for testing"""
    return [
        sample_trend,
        Trend(
            id="sample_id_456",
            title="Another Sample Trend",
            url="https://example.com/another",
            source="hn",
            score=200,
            ts=datetime(2022, 1, 1, 13, 0, 0)
        ),
        Trend(
            id="sample_id_789",
            title="Third Sample Trend",
            url=None,  # Test with missing URL
            source="hn",
            score=75,
            ts=datetime(2022, 1, 1, 14, 0, 0)
        )
    ]
