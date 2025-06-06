# ビルドステージ
FROM python:3.10-slim as builder

WORKDIR /app

# テスト用の依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest pytest-asyncio pytest-cov

# テスト用のソースコードをコピー
COPY ./src ./src
COPY ./tests ./tests

# テスト実行（全体）
RUN pytest tests/ -v
# モックテストのみ実行できるように追加
RUN pytest tests/test_mock_planner_agent.py -v

# --- 本番用ステージは一旦コメントアウト ---
# FROM python:3.10-slim
# RUN groupadd -r appuser && useradd -r -g appuser appuser
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY ./src ./src
# ENV PYTHONPATH=/app
# ENV PYTHONUNBUFFERED=1
# USER appuser
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD python -c "import src.mcp_server_time; src.mcp_server_time.get_current_time()"
# ENTRYPOINT ["python", "-m", "src.planner_agent"] 