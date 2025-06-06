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

# テスト実行
RUN pytest tests/ -v

# 本番用ステージ
FROM python:3.10-slim

# セキュリティのため、root以外のユーザーを作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 本番用の依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 本番用のソースコードをコピー
COPY ./src ./src

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# セキュリティのため、非rootユーザーに切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import src.mcp_server_time; src.mcp_server_time.get_current_time()"

# エントリーポイント
ENTRYPOINT ["python", "-m", "src.planner_agent"] 