FROM python:3.10-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest pytest-asyncio httpx pytest-cov python-dotenv

# ソースコードをコピー
COPY src/ ./src/
COPY tests/ ./tests/

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONIOENCODING=utf-8

# テスト実行用のエントリーポイント
ENTRYPOINT ["pytest"]
CMD ["-v"] 