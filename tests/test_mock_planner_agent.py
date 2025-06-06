import pytest
from unittest.mock import patch
from io import StringIO
import asyncio
from mock_planner_agent import mock_main

@pytest.mark.asyncio
async def test_mock_planner_agent():
    # 標準入力をモック
    test_input = "Spotifyで音楽を検索して"
    with patch('sys.stdin', StringIO(test_input + '\nquit\n')):
        # 標準出力をキャプチャ
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # 期待される出力の検証
            assert "モックのmain関数が呼び出されました" in output
            assert "AIアシスタントが起動しました" in output
            assert "モックの応答:" in output
            assert "AIアシスタントを終了します" in output

@pytest.mark.asyncio
async def test_mock_planner_agent_empty_input():
    # 空の入力をテスト
    with patch('sys.stdin', StringIO('\nquit\n')):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # 空の入力がスキップされることを確認
            assert "質問を入力してください" in output
            assert "モックの応答:" not in output

@pytest.mark.asyncio
async def test_mock_planner_agent_exit_command():
    # 終了コマンドのテスト
    with patch('sys.stdin', StringIO('exit\n')):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # 終了メッセージが表示されることを確認
            assert "AIアシスタントを終了します" in output

@pytest.mark.asyncio
async def test_mock_planner_agent_spotify_search():
    # Spotify検索のテスト
    test_input = "Spotifyで「Shape of You」を検索して"
    with patch('sys.stdin', StringIO(test_input + '\nquit\n')):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # Spotify検索の呼び出しを確認
            assert "Spotify検索が呼び出されました" in output
            assert "Shape of You" in output
            assert "モックの応答:" in output

@pytest.mark.asyncio
async def test_mock_planner_agent_web_search():
    # Web検索のテスト
    test_input = "Pythonの最新バージョンについて検索して"
    with patch('sys.stdin', StringIO(test_input + '\nquit\n')):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # Web検索の呼び出しを確認
            assert "Web検索が呼び出されました" in output
            assert "Python" in output
            assert "モックの応答:" in output

@pytest.mark.asyncio
async def test_mock_planner_agent_time():
    # 時刻取得のテスト
    test_input = "今の時刻を教えて"
    with patch('sys.stdin', StringIO(test_input + '\nquit\n')):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            await mock_main()
            output = mock_stdout.getvalue()
            
            # 時刻取得の呼び出しを確認
            assert "現在時刻の取得が呼び出されました" in output
            assert "モックの応答:" in output 