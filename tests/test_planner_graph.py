import pytest
from langgraph.graph import Graph
from graphs.planner_graph import create_planner_graph

def test_planner_graph_creation():
    """プランナーグラフの作成テスト"""
    graph = create_planner_graph()
    assert isinstance(graph, Graph)
    assert len(graph.nodes) > 0

def test_planner_graph_execution():
    """プランナーグラフの実行テスト"""
    graph = create_planner_graph()
    result = graph.run({
        "task": "週末のスポットを探す",
        "location": "東京",
        "date": "2024-03-30"
    })
    assert result is not None
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0 