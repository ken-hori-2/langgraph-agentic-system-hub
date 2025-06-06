import pytest
from unittest.mock import patch
from src.mcp_server_search import search_web

def test_search_web_basic():
    """Test basic web search functionality"""
    with patch('src.mcp_server_search.tavily_search') as mock_search:
        mock_search.return_value = {"results": [{"title": "Test Result", "content": "Test Content"}]}
        result = search_web("test query")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Test Result" in result
        assert "Test Content" in result

def test_search_web_empty_query():
    """Test search with empty query"""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        search_web("")

def test_search_web_error_handling():
    """Test search error handling"""
    with patch('src.mcp_server_search.tavily_search') as mock_search:
        mock_search.side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            search_web("test query") 