import pytest
import httpx
from tools.spotify_mcp import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_spotify_search():
    """Spotify検索エンドポイントのテスト"""
    response = client.post("/search", json={
        "query": "test song",
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "tracks" in data
    assert len(data["tracks"]) <= 5

def test_spotify_playback():
    """Spotify再生エンドポイントのテスト"""
    response = client.post("/play", json={
        "track_id": "test_track_id"
    })
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success" 