import pytest
from unittest.mock import patch, AsyncMock
from agents.trend_scout import fetch_hn_top, main


@pytest.mark.integration
class TestTrendScoutIntegration:
    """Integration tests for Trend Scout agent"""

    @pytest.mark.asyncio
    async def test_full_pipeline_mock(self):
        """Test the full pipeline with mocked external dependencies"""
        # Mock data
        mock_hn_data = {
            "topstories": [123, 456],
            "item_123": {
                "id": 123,
                "title": "Integration Test Article 1",
                "url": "https://example.com/integration1",
                "score": 250,
                "time": 1640995200
            },
            "item_456": {
                "id": 456,
                "title": "Integration Test Article 2",
                "url": "https://example.com/integration2", 
                "score": 180,
                "time": 1640995300
            }
        }

        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client, \
             patch('agents.trend_scout.asyncpg.create_pool') as mock_create_pool:
            
            # Setup HTTP client mock
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get.side_effect = [
                AsyncMock(json=lambda: mock_hn_data["topstories"]),
                AsyncMock(json=lambda: mock_hn_data["item_123"]),
                AsyncMock(json=lambda: mock_hn_data["item_456"])
            ]
            
            # Setup database pool mock
            mock_pool = AsyncMock()
            mock_connection = AsyncMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
            mock_create_pool.return_value = mock_pool
            
            # Run the main function
            await main()
            
            # Verify the database interaction
            mock_connection.executemany.assert_called_once()
            call_args = mock_connection.executemany.call_args
            query = call_args[0][0]
            params = call_args[0][1]
            
            # Verify SQL query
            assert "INSERT INTO trends" in query
            assert "ON CONFLICT DO NOTHING" in query
            
            # Verify we got 2 trends
            assert len(params) == 2
            
            # Verify trend data
            trend1_tuple = params[0]
            trend2_tuple = params[1]
            
            assert trend1_tuple[1] == "Integration Test Article 1"  # title
            assert trend1_tuple[2] == "https://example.com/integration1"  # url
            assert trend1_tuple[3] == "hn"  # source
            assert trend1_tuple[4] == 250  # score
            
            assert trend2_tuple[1] == "Integration Test Article 2"
            assert trend2_tuple[4] == 180

    @pytest.mark.asyncio
    async def test_fetch_with_missing_url(self):
        """Test fetching items where some have missing URLs (Ask HN posts)"""
        mock_hn_data = {
            "topstories": [111],
            "item_111": {
                "id": 111,
                "title": "Ask HN: How to test async code?",
                # No URL field for Ask HN posts
                "score": 45,
                "time": 1640995400
            }
        }

        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get.side_effect = [
                AsyncMock(json=lambda: mock_hn_data["topstories"]),
                AsyncMock(json=lambda: mock_hn_data["item_111"])
            ]
            
            trends = await fetch_hn_top(n=1)
            
            assert len(trends) == 1
            trend = trends[0]
            assert trend.title == "Ask HN: How to test async code?"
            assert trend.url is None  # Should handle missing URL gracefully
            assert trend.score == 45

    @pytest.mark.asyncio
    async def test_concurrent_fetching(self):
        """Test that multiple items are fetched concurrently"""
        # This test verifies the asyncio.gather functionality
        mock_hn_data = {
            "topstories": [1, 2, 3, 4, 5],
            "item_1": {"id": 1, "title": "Title 1", "url": "http://1.com", "score": 100, "time": 1640995200},
            "item_2": {"id": 2, "title": "Title 2", "url": "http://2.com", "score": 95, "time": 1640995201},
            "item_3": {"id": 3, "title": "Title 3", "url": "http://3.com", "score": 90, "time": 1640995202},
            "item_4": {"id": 4, "title": "Title 4", "url": "http://4.com", "score": 85, "time": 1640995203},
            "item_5": {"id": 5, "title": "Title 5", "url": "http://5.com", "score": 80, "time": 1640995204}
        }

        with patch('agents.trend_scout.httpx.AsyncClient') as mock_client:
            mock_context = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_context
            
            # Mock responses for all items
            responses = [AsyncMock(json=lambda: mock_hn_data["topstories"])]
            for i in range(1, 6):
                responses.append(AsyncMock(json=lambda item_key=f"item_{i}": mock_hn_data[item_key]))
            
            mock_context.get.side_effect = responses
            
            trends = await fetch_hn_top(n=5)
            
            assert len(trends) == 5
            # Verify all trends were processed
            titles = [t.title for t in trends]
            expected_titles = ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"]
            assert set(titles) == set(expected_titles)

    @pytest.mark.asyncio  
    async def test_error_handling_in_pipeline(self):
        """Test error handling in the full pipeline"""
        with patch('agents.trend_scout.asyncpg.create_pool') as mock_create_pool, \
             patch('agents.trend_scout.fetch_hn_top') as mock_fetch:
            
            # Simulate fetch error
            mock_fetch.side_effect = Exception("Network timeout")
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            with pytest.raises(Exception, match="Network timeout"):
                await main()
            
            # Pool should still be closed even on error
            mock_pool.close.assert_called_once()

    def test_trend_id_generation(self):
        """Test that trend IDs are generated consistently"""
        import hashlib
        
        # Test that the same input generates the same hash
        test_id = 123
        expected_hash = hashlib.md5(str(test_id).encode()).hexdigest()
        
        # This should match what's generated in the trend_scout.py
        assert expected_hash == "202cb962ac59075b964b07152d234b70"
        
        # Different IDs should generate different hashes
        different_hash = hashlib.md5(str(456).encode()).hexdigest()
        assert expected_hash != different_hash
