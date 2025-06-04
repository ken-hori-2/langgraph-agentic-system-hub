import pytest
import httpx
from fastapi.testclient import TestClient
from tools.spotify_mcp import app as spotify_app
from tools.weather_mcp import app as weather_app
from graphs.planner_graph import create_planner_graph

spotify_client = TestClient(spotify_app)
weather_client = TestClient(weather_app)

def test_end_to_end_weekend_planning():
    """週末プランニングのエンドツーエンドテスト"""
    # 1. 天気情報の取得
    weather_response = weather_client.get("/forecast", params={
        "location": "東京",
        "date": "2024-03-30"
    })
    assert weather_response.status_code == 200
    weather_data = weather_response.json()
    
    # 2. スポット検索
    spotify_response = spotify_client.post("/search", json={
        "query": "週末 東京 おすすめ",
        "limit": 5
    })
    assert spotify_response.status_code == 200
    spotify_data = spotify_response.json()
    
    # 3. LangGraphによる統合
    graph = create_planner_graph()
    result = graph.run({
        "task": "週末のスポットを探す",
        "location": "東京",
        "date": "2024-03-30",
        "weather": weather_data,
        "music_recommendations": spotify_data
    })
    
    assert result is not None
    assert "recommendations" in result
    assert "weather_advice" in result
    assert "music_suggestions" in result 