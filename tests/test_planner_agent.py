import pytest
from unittest.mock import patch, MagicMock
from src.planner_agent import PlannerAgent

@pytest.fixture
def mock_agent():
    """Create a PlannerAgent instance with mocked dependencies"""
    with patch('src.planner_agent.get_current_time') as mock_time, \
         patch('src.planner_agent.search_web') as mock_search, \
         patch('src.planner_agent.get_spotify_recommendations') as mock_spotify:
        mock_time.return_value = "2024-03-15 12:00:00"
        mock_search.return_value = "Search results for test query"
        mock_spotify.return_value = ["Track 1", "Track 2"]
        agent = PlannerAgent()
        yield agent

def test_planner_agent_initialization(mock_agent):
    """Test if PlannerAgent can be initialized"""
    assert mock_agent is not None

def test_planner_agent_process_time_task(mock_agent):
    """Test if PlannerAgent can process a time-related task"""
    result = mock_agent.process_task("Get current time")
    assert isinstance(result, str)
    assert "2024-03-15" in result
    assert "12:00" in result

def test_planner_agent_process_search_task(mock_agent):
    """Test if PlannerAgent can process a search-related task"""
    result = mock_agent.process_task("Search for AI news")
    assert isinstance(result, str)
    assert "Search results" in result

def test_planner_agent_process_music_task(mock_agent):
    """Test if PlannerAgent can process a music-related task"""
    result = mock_agent.process_task("Get pop music recommendations")
    assert isinstance(result, str)
    assert "Track 1" in result
    assert "Track 2" in result

def test_planner_agent_invalid_task(mock_agent):
    """Test PlannerAgent with invalid task"""
    with pytest.raises(ValueError, match="Task cannot be empty"):
        mock_agent.process_task("")

def test_planner_agent_complex_task(mock_agent):
    """Test PlannerAgent with a complex task requiring multiple tools"""
    result = mock_agent.process_task("Get current time and search for AI news")
    assert isinstance(result, str)
    assert "2024-03-15" in result
    assert "Search results" in result 