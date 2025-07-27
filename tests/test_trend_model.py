from typing import Any
import pytest
from datetime import datetime
from pydantic import ValidationError
from common.types import Trend


class TestTrendModel:
    """Test cases for the Trend data model"""

    def test_trend_creation_with_all_fields(self):
        """Test creating a Trend with all fields"""
        trend = Trend(
            id="test_123",
            title="Test Article",
            url="https://example.com/test",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1, 12, 0, 0)
        )
        
        assert trend.id == "test_123"
        assert trend.title == "Test Article"
        assert trend.url == "https://example.com/test"
        assert trend.source == "hn"
        assert trend.score == 100
        assert trend.ts == datetime(2022, 1, 1, 12, 0, 0)

    def test_trend_creation_without_url(self):
        """Test creating a Trend without URL (Ask HN posts)"""
        trend = Trend(
            id="test_456",
            title="Ask HN: How to test?",
            url=None,
            source="hn",
            score=50,
            ts=datetime(2022, 1, 1, 12, 0, 0)
        )
        
        assert trend.id == "test_456"
        assert trend.title == "Ask HN: How to test?"
        assert trend.url is None
        assert trend.source == "hn"
        assert trend.score == 50

    def test_trend_creation_url_default(self):
        """Test creating a Trend without specifying URL (should default to None)"""
        trend = Trend(
            id="test_789",
            title="Default URL Test",
            source="hn",
            score=75,
            ts=datetime(2022, 1, 1, 12, 0, 0)
        )
        
        assert trend.url is None

    def test_trend_tuple_method(self):
        """Test the tuple() method returns correct values in correct order"""
        trend = Trend(
            id="tuple_test",
            title="Tuple Test Article",
            url="https://example.com/tuple",
            source="hn",
            score=200,
            ts=datetime(2022, 6, 15, 14, 30, 45)
        )
        
        expected_tuple = (
            "tuple_test",
            "Tuple Test Article", 
            "https://example.com/tuple",
            "hn",
            200,
            datetime(2022, 6, 15, 14, 30, 45)
        )
        
        assert trend.tuple() == expected_tuple

    def test_trend_tuple_method_with_none_url(self):
        """Test tuple() method when URL is None"""
        trend = Trend(
            id="none_url_test",
            title="None URL Test",
            url=None,
            source="hn",
            score=150,
            ts=datetime(2022, 12, 25, 0, 0, 0)
        )
        
        expected_tuple = (
            "none_url_test",
            "None URL Test",
            None,
            "hn", 
            150,
            datetime(2022, 12, 25, 0, 0, 0)
        )
        
        assert trend.tuple() == expected_tuple

    def test_trend_validation_required_fields(self):
        """Test that required fields are validated"""
        with pytest.raises(ValidationError) as exc_info:
            Trend.model_validate({})
        
        # Should fail because id, title, source, score, and ts are required
        error = exc_info.value
        error_dict = error.errors()
        required_fields = {err['loc'][0] for err in error_dict if err['type'] == 'missing'}
        expected_required = {'id', 'title', 'source', 'score', 'ts'}
        assert required_fields == expected_required

    def test_trend_validation_missing_title(self):
        """Test validation fails when title is missing"""
        with pytest.raises(ValidationError) as exc_info:
            Trend.model_validate({
                "id": "missing_title_test",
                "source": "hn",
                "score": 100,
                "ts": datetime.now()
            })
        
        error = exc_info.value
        assert any(err['loc'] == ('title',) for err in error.errors())

    def test_trend_validation_invalid_score_type(self):
        """Test validation fails with invalid score type"""
        with pytest.raises(ValidationError) as exc_info:
            Trend(
                id="invalid_score",
                title="Invalid Score Test",
                source="hn",
                score="not_a_number", # type: ignore  # Should be int
                ts=datetime.now()
            )
        
        error = exc_info.value
        assert any(err['loc'] == ('score',) for err in error.errors())

    def test_trend_validation_invalid_datetime_type(self):
        """Test validation fails with invalid datetime type"""
        with pytest.raises(ValidationError) as exc_info:
            Trend(
                id="invalid_datetime",
                title="Invalid Datetime Test",
                source="hn",
                score=100,
                ts="not_a_datetime" # type: ignore  # Should be datetime
            )
        
        error = exc_info.value
        assert any(err['loc'] == ('ts',) for err in error.errors())

    def test_trend_equality(self):
        """Test that Trends with same data are equal"""
        trend1 = Trend(
            id="equal_test",
            title="Equality Test",
            url="https://example.com/equal",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        trend2 = Trend(
            id="equal_test",
            title="Equality Test",
            url="https://example.com/equal",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        assert trend1 == trend2

    def test_trend_inequality(self):
        """Test that Trends with different data are not equal"""
        trend1 = Trend(
            id="unequal_test_1",
            title="First Trend",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        trend2 = Trend(
            id="unequal_test_2",
            title="Second Trend",
            source="hn",
            score=100,
            ts=datetime(2022, 1, 1)
        )
        
        assert trend1 != trend2

    def test_trend_json_serialization(self):
        """Test that Trend can be serialized to JSON"""
        trend = Trend(
            id="json_test",
            title="JSON Test Article",
            url="https://example.com/json",
            source="hn",
            score=300,
            ts=datetime(2022, 5, 10, 16, 20, 30)
        )
        
        # Test model_dump (Pydantic v2)
        json_data = trend.model_dump()
        
        assert json_data['id'] == "json_test"
        assert json_data['title'] == "JSON Test Article"
        assert json_data['url'] == "https://example.com/json"
        assert json_data['source'] == "hn"
        assert json_data['score'] == 300
        assert json_data['ts'] == datetime(2022, 5, 10, 16, 20, 30)

    def test_trend_from_dict(self):
        """Test creating Trend from dictionary"""
        data: dict[str, Any] = {
            'id': 'dict_test',
            'title': 'Dict Test Article',
            'url': 'https://example.com/dict',
            'source': 'hn',
            'score': 250,
            'ts': datetime(2022, 8, 20, 10, 15, 0)
        }
        
        trend = Trend(**data)
        
        assert trend.id == "dict_test"
        assert trend.title == "Dict Test Article"
        assert trend.url == "https://example.com/dict"
        assert trend.source == "hn"
        assert trend.score == 250
        assert trend.ts == datetime(2022, 8, 20, 10, 15, 0)
