import pytest
from unittest.mock import patch
from datetime import datetime
from src.mcp_server_time import get_current_time

def test_get_current_time_format():
    """Test if get_current_time returns a properly formatted time string"""
    with patch('src.mcp_server_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 15, 12, 0, 0)
        time_str = get_current_time()
        assert isinstance(time_str, str)
        assert len(time_str) > 0
        assert "2024" in time_str
        assert "12:00" in time_str

def test_get_current_time_consistency():
    """Test if get_current_time returns consistent results within a short time frame"""
    with patch('src.mcp_server_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 15, 12, 0, 0)
        time1 = get_current_time()
        time2 = get_current_time()
        assert time1 == time2 