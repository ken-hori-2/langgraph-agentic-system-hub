import pytest
from src.mcp_server_time import get_current_time
from src.mcp_server_search import search_web
from src.mcp_server_spotify import get_spotify_recommendations
from src.planner_agent import PlannerAgent

def test_get_current_time():
    """Test if get_current_time returns a string"""
    time_str = get_current_time()
    assert isinstance(time_str, str)
    assert len(time_str) > 0

def test_search_web():
    """Test if search_web returns a string"""
    result = search_web("test query")
    assert isinstance(result, str)
    assert len(result) > 0

def test_spotify_recommendations():
    """Test if get_spotify_recommendations returns a list"""
    recommendations = get_spotify_recommendations("test genre")
    assert isinstance(recommendations, list)

def test_planner_agent_initialization():
    """Test if PlannerAgent can be initialized"""
    agent = PlannerAgent()
    assert agent is not None 