import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # テスト用の環境変数を設定
    test_env = {
        "OPENAI_API_KEY": "test_key",
        "TAVILY_API_KEY": "test_key",
        "SPOTIFY_USER_ID": "test_user",
        "SPOTIFY_TOKEN": "test_token"
    }
    
    # 既存の環境変数をバックアップ
    original_env = {}
    for key in test_env:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    # テスト用の環境変数を設定
    for key, value in test_env.items():
        os.environ[key] = value
    
    # .envファイルがあれば読み込む
    load_dotenv()
    
    yield
    
    # 環境変数を元に戻す
    for key in test_env:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            del os.environ[key] 