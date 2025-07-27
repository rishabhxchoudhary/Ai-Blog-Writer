import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from agents.trend_scout import fetch_hn_top, persist, main
from common.types import Trend


@pytest.fixture
def mock_hn_response():
    """Mock response data from Hacker News API"""
    return {
        "topstories": [1, 2, 3],
        "item_1": {
            "id": 1,
            "title": "Test Article 1",
            "url": "https://example.com/1",
            "score": 100,
            "time": 1640995200  # 2022-01-01 00:00:00 UTC
        },
        "item_2": {
            "id": 2,
            "title": "Test Article 2",
            "url": "https://example.com/2",
            "score": 75,
            "time": 1640995260  # 2022-01-01 00:01:00 UTC
        },
        "item_3": {
            "id": 3,
            "title": "Test Article 3",
            "url": "https://example.com/3",
            "score": 50,
            "time": 1640995320  # 2022-01-01 00:02:00 UTC
        }
    }


@pytest.fixture
def expected_trends():
    """Expected Trend objects from mock data"""
    return [
        Trend(
            id="c4ca4238a0b923820dcc509a6f75849b",  # md5 hash of "1"
            title="Test Article 1",
            url="https://example.com/1",
            source="hn",
            score=100,
            ts=datetime.utcfromtimestamp(1640995200)
        ),
        Trend(
            id="c81e728d9d4c2f636f067f89cc14862c",  # md5 hash of "2"
            title="Test Article 2",
            url="https://example.com/2",
            source="hn",
            score=75,
            ts=datetime.utcfromtimestamp(1640995260)
        ),
        Trend(
            id="eccbc87e4b5ce2fe28308fd9f2a7baf3",  # md5 hash of "3"
            title="Test Article 3",
            url="https://example.com/3",
            source="hn",
            score=50,
            ts=datetime.utcfromtimestamp(1640995320)
        )
    ]


class TestFetchHnTop:
    """Test cases for fetch_hn_top function"""

    @pytest.mark.asyncio
    async def test_fetch_hn_top_success(self, mock_hn_response, expected_trends):
        """Test successful fetching of top stories from Hacker News"""
        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            # Setup mock client
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            
            # Mock API responses
            mock_context.get.side_effect = [
                # First call: get top stories
                AsyncMock(json=lambda: mock_hn_response["topstories"]),
                # Subsequent calls: get individual items
                AsyncMock(json=lambda: mock_hn_response["item_1"]),
                AsyncMock(json=lambda: mock_hn_response["item_2"]),
                AsyncMock(json=lambda: mock_hn_response["item_3"])
            ]
            
            # Call the function
            result = await fetch_hn_top(n=3)
            
            # Verify results
            assert len(result) == 3
            assert all(isinstance(trend, Trend) for trend in result)
            
            # Check specific values
            for i, trend in enumerate(result):
                expected = expected_trends[i]
                assert trend.id == expected.id
                assert trend.title == expected.title
                assert trend.url == expected.url
                assert trend.source == "hn"
                assert trend.score == expected.score
                assert trend.ts == expected.ts

    @pytest.mark.asyncio
    async def test_fetch_hn_top_with_different_n(self, mock_hn_response):
        """Test fetching with different number of stories"""
        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            
            # Mock response with only first 2 items
            mock_context.get.side_effect = [
                AsyncMock(json=lambda: mock_hn_response["topstories"][:2]),
                AsyncMock(json=lambda: mock_hn_response["item_1"]),
                AsyncMock(json=lambda: mock_hn_response["item_2"])
            ]
            
            result = await fetch_hn_top(n=2)
            
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_fetch_hn_top_api_error(self):
        """Test handling of API errors"""
        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            
            # Mock API error
            mock_context.get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                await fetch_hn_top()

    @pytest.mark.asyncio
    async def test_fetch_hn_top_missing_fields(self):
        """Test handling of items with missing fields"""
        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            
            # Mock response with missing url field
            incomplete_item = {
                "id": 1,
                "title": "Test Article",
                # "url": missing
                "score": 100,
                "time": 1640995200
            }
            
            mock_context.get.side_effect = [
                AsyncMock(json=lambda: [1]),
                AsyncMock(json=lambda: incomplete_item)
            ]
            
            with pytest.raises(KeyError):
                await fetch_hn_top(n=1)


class TestPersist:
    """Test cases for persist function"""

    @pytest.mark.asyncio
    async def test_persist_success(self, expected_trends):
        """Test successful persistence of trends to database"""
        # Mock database pool and connection
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        await persist(mock_pool, expected_trends)
        
        # Verify database interaction
        mock_pool.acquire.assert_called_once()
        mock_connection.executemany.assert_called_once()
        
        # Check the SQL query and parameters
        call_args = mock_connection.executemany.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "insert into trends" in query.lower()
        assert "on conflict do nothing" in query.lower()
        assert len(params) == 3  # 3 trends
        
        # Verify parameters match expected trends
        for i, trend_tuple in enumerate(params):
            expected_tuple = expected_trends[i].tuple()
            assert trend_tuple == expected_tuple

    @pytest.mark.asyncio
    async def test_persist_empty_list(self):
        """Test persistence with empty trends list"""
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        await persist(mock_pool, [])
        
        # Should still call executemany with empty list
        mock_connection.executemany.assert_called_once()
        call_args = mock_connection.executemany.call_args
        params = call_args[0][1]
        assert params == []

    @pytest.mark.asyncio
    async def test_persist_database_error(self, expected_trends):
        """Test handling of database errors during persistence"""
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.executemany.side_effect = Exception("Database Error")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        with pytest.raises(Exception, match="Database Error"):
            await persist(mock_pool, expected_trends)


class TestMain:
    """Test cases for main function"""

    @pytest.mark.asyncio
    async def test_main_integration(self, mock_hn_response):
        """Test the main function integration"""
        with patch('agents.trend_scout.asyncpg.create_pool') as mock_create_pool, \
             patch('agents.trend_scout.fetch_hn_top') as mock_fetch, \
             patch('agents.trend_scout.persist') as mock_persist:
            
            # Setup mocks
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            mock_trends = [
                Trend(
                    id="test_id",
                    title="Test Title",
                    url="https://example.com",
                    source="hn",
                    score=100,
                    ts=datetime.now()
                )
            ]
            mock_fetch.return_value = mock_trends
            
            # Call main
            await main()
            
            # Verify calls
            mock_create_pool.assert_called_once_with(dsn="postgresql://blog:pw@localhost/blog")
            mock_fetch.assert_called_once()
            mock_persist.assert_called_once_with(mock_pool, mock_trends)

    @pytest.mark.asyncio
    async def test_main_fetch_error(self):
        """Test main function when fetch fails"""
        with patch('agents.trend_scout.asyncpg.create_pool') as mock_create_pool, \
             patch('agents.trend_scout.fetch_hn_top') as mock_fetch:
            
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            mock_fetch.side_effect = Exception("Fetch Error")
            
            with pytest.raises(Exception, match="Fetch Error"):
                await main()

    @pytest.mark.asyncio
    async def test_main_persist_error(self):
        """Test main function when persist fails"""
        with patch('agents.trend_scout.asyncpg.create_pool') as mock_create_pool, \
             patch('agents.trend_scout.fetch_hn_top') as mock_fetch, \
             patch('agents.trend_scout.persist') as mock_persist:
            
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            mock_fetch.return_value = []
            mock_persist.side_effect = Exception("Persist Error")
            
            with pytest.raises(Exception, match="Persist Error"):
                await main()


class TestTrendModel:
    """Test cases for Trend model"""

    def test_trend_creation(self):
        """Test creating a Trend object"""
        trend = Trend(
            id="test_id",
            title="Test Title",
            url="https://example.com",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        assert trend.id == "test_id"
        assert trend.title == "Test Title"
        assert trend.url == "https://example.com"
        assert trend.source == "hn"
        assert trend.score == 100
        assert trend.ts == datetime(2022, 1, 1)

    def test_trend_tuple_method(self):
        """Test the tuple method of Trend"""
        trend = Trend(
            id="test_id",
            title="Test Title",
            url="https://example.com",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        expected_tuple = ("test_id", "Test Title", "https://example.com", "hn", 100, datetime(2022, 1, 1))
        assert trend.tuple() == expected_tuple

    def test_trend_optional_url(self):
        """Test Trend with optional URL"""
        trend = Trend(
            id="test_id",
            title="Test Title",
            url=None,
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        assert trend.url is None
        expected_tuple = ("test_id", "Test Title", None, "hn", 100, datetime(2022, 1, 1))
        assert trend.tuple() == expected_tuple
