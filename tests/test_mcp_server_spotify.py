import pytest
from unittest.mock import patch
from src.mcp_server_spotify import get_spotify_recommendations

def test_spotify_recommendations_basic():
    """Test basic Spotify recommendations functionality"""
    with patch('src.mcp_server_spotify.spotipy.Spotify') as mock_spotify:
        mock_spotify.return_value.recommendations.return_value = {
            "tracks": [
                {"name": "Test Track 1", "artists": [{"name": "Artist 1"}]},
                {"name": "Test Track 2", "artists": [{"name": "Artist 2"}]}
            ]
        }
        recommendations = get_spotify_recommendations("pop")
        assert isinstance(recommendations, list)
        assert len(recommendations) == 2
        assert "Test Track 1" in recommendations[0]
        assert "Artist 1" in recommendations[0]

def test_spotify_recommendations_empty_genre():
    """Test recommendations with empty genre"""
    with pytest.raises(ValueError, match="Genre cannot be empty"):
        get_spotify_recommendations("")

def test_spotify_recommendations_error_handling():
    """Test Spotify API error handling"""
    with patch('src.mcp_server_spotify.spotipy.Spotify') as mock_spotify:
        mock_spotify.return_value.recommendations.side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            get_spotify_recommendations("pop") 