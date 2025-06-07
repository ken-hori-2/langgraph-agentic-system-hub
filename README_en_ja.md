# LangGraph Agentic System Hub

🧠 A modular and extensible framework for building multi-agent LLM applications using LangGraph and MCP tools.

---

## 🔥 Overview

This project provides a **LangGraph-based agentic architecture** that integrates various tools (e.g. weather, Spotify, Google Maps, etc.) via **MCP (Modular Command Protocol)** to enable intelligent and dynamic task execution.

It is designed to support:
- 🗺️ Weekend spot planning with web search & map tools
- 🍻 Party venue search with availability checks (HotPepper, Tabelog)
- 🎧 Spotify music search & playback based on requests
- ✅ Task management using calendar & to-do tools
- 🎯 A unified orchestrator to route tasks to the best agent

---

## 🏗️ Project Structure
<!--
langgraph-agentic-system-hub/
├── README.md
├── requirements.txt
├── main.py
├── /agents
│   ├── orchestrator.py         # Routes tasks to the appropriate agent
│   ├── music_agent.py
│   ├── event_agent.py
│   └── weather_agent.py
├── /tools
│   ├── spotify_mcp.py          # MCP server for Spotify search
│   ├── weather_mcp.py          # MCP server for weather info
│   ├── map_search_mcp.py       # Google Maps, HotPepper, Tabelog
│   └── calendar_mcp.py         # Google Calendar/Todo (future)
├── /graphs
│   └── planner_graph.py        # LangGraph workflow (multi-agent)
├── /tests
│   └── test_spotify_mcp.py
-->

```txt
langgraph-agentic-system-hub/
├── README.md                  # このプロジェクトのドキュメント
├── requirements.txt           # 依存ライブラリ一覧
├── main.py                    # アプリのエントリーポイント
│
├── agents/                    # 各エージェントのLangGraphノード処理
│   ├── orchestrator.py        # タスクを適切なエージェントに振り分ける中核エージェント
│   ├── music_agent.py         # Spotifyなど音楽系の処理を担うエージェント
│   ├── event_agent.py         # 飲み会や週末スポット提案用のエージェント
│   └── weather_agent.py       # 天気情報を取得するエージェント
│
├── tools/                     # 各種外部ツール（FastMCP）との連携サーバー
│   ├── spotify_mcp.py         # Spotify楽曲検索用 MCP サーバー
│   ├── weather_mcp.py         # 天気API取得用 MCP サーバー
│   ├── map_search_mcp.py      # Google Maps / HotPepper / 食べログ連携（飲み会検索）
│   └── calendar_mcp.py        # Google Calendar / TODO管理（今後追加予定）
│
├── graphs/                    # LangGraph フロー定義
│   └── planner_graph.py       # マルチエージェント連携ワークフローの定義
│
├── memory/                    # LangChain Memory 機能（会話履歴保持）
│   └── memory_config.py       # 記憶の保存/復元の定義（例：ChatMessageHistory）
│
├── ui/                        # ユーザーインターフェース（例：Gradioなど）
│   └── web_ui.py              # Webベースの対話インターフェース（開発中）
│
├── tests/                     # ツールやエージェントの動作確認用テスト
│   └── test_spotify_mcp.py    # Spotify MCP の動作テスト
│
└── docs/                      # アーキテクチャ設計資料やユースケースまとめ
    └── architecture.png       # 全体構成図やフロー図など
```

---

## 🔧 Requirements
```txt
langchain
langgraph
openai
mcp
fastapi
spotipy
python-dotenv
aiohttp
gradio
```

<!--
## 🗂️ `requirements.txt` 例（ベース）
```txt
langgraph
mcp
openai
spotipy
python-dotenv
fastapi
uvicorn
aiohttp
```
-->
pip install -r requirements.txt で一括インストールできます。

## 🚀 Getting Started

### 1. Clone & install dependencies

```bash
git clone https://github.com/kenji/langgraph-agentic-system-hub.git
cd langgraph-agentic-system-hub
pip install -r requirements.txt
```
<!-- ## 📦 How to Run -->
### 2. Run a tool MCP server
```bash
python tools/spotify_mcp.py
# or
python tools/weather_mcp.py
```

### 3. Run the LangGraph agent
```bash
python main.py
```

### 4. Gradio UIを起動（今後追加）
```bash
python ui/web_ui.py
```

## 🧩 Agentic Workflow Example
```txt
User: 「週末に行けそうな場所を探して」
→ Orchestrator: "PlannerAgent" へルーティング
→ PlannerAgent: Web検索用MCPを利用
→ Google Maps MCP + HotPepper MCP から情報取得
→ 結果をLangGraph経由でユーザーに返す
```

## 🔮 Future Plans
- 🧠 Memory integration with LangChain memory
- 🔍 RAG (Retrieval-Augmented Generation) for dynamic search
- 📆 Google Calendar連携で予定の自動調整
- 📎 Notionへの自動まとめ機能
- 🎤 YouTube音源分離ツールとの連携
- 💬 Agent毎の専門プロンプト最適化
- 🗺️ LangGraph SDK による視覚的ワークフロー生成

<!--
## 🔮 Future Extensions
- 💬 LangChain Memory によるチャット履歴の保持
- 🔍 RAG によるリアルタイムWeb検索（ニュース、週末スポットなど）
- 🧠 Agent毎の専門プロンプト最適化
- 🗺️ LangGraph SDK による視覚的ワークフロー生成
-->

## ✨ Example Use Cases
| ユースケース       | 概要                                                                 |
|--------------------|----------------------------------------------------------------------|
| 🎵 音楽検索         | ユーザーの希望に応じて Spotify から楽曲検索・推薦を行います。              |
| 🍺 飲み会番長       | 人数・日付・エリアに基づいて、良いお店を探して空席状況をチェックします。     |
| 🌤 天気確認         | 現在地や指定されたエリアの天気情報を取得し、アドバイスを提供します。         |
| 📆 タスク管理       | Google Calendar と連携して、予定の確認や ToDo リストの管理を行います。       |
| 📍 お出かけ提案     | 人気の週末スポットやレビューを取得して、行き先をおすすめします。             |

## 👤 Author
**Centaurus-Ken（[@ken-hori-2](https://github.com/ken-hori-2)）**

LangGraph × MCP による Agentic AI システムの実験・開発を行う開発者。  
普段は「こんなアプリがあったらいいな」という日常の願望を起点に、Agentic AI のコンセプト立案からマルチエージェント構成でのデモ開発・プレゼンまで幅広く担当。
また、センシングデバイス上で動作するエッジ AI モデルの設計・構築、デモ開発にも従事しており、CI/CD パイプラインの構築やテスト自動化の経験も保有。
今後はさらに多様なユースケース（音楽、天気、飲み会、予定管理など）に対応する Agentic AI Hub としての機能拡張を目指しています。

<!--
Author
Centaurus-Ken（@ken-hori-2）
LangGraph + MCP による Agentic AI 実験者。
今後さらに多くのユースケースに対応予定です。
-->

## 📄 License

MIT License.

Created by Centaurus-Ken for exploring next-gen LLM applications with modular tool orchestration.

---

## Appendix: FastAPI + Uvicorn MCP Agent API Example

このリポジトリには、FastAPIとUvicornを用いたMCPエージェントAPIのサンプル実装も含まれています。

### ディレクトリ構成

```
src/uv_agent_api/
  ├── uv_api_agent.py   # Agent本体（LangGraph/LLM/Tool定義）
  ├── uv_api_main.py    # FastAPIサーバー起動用
  └── uv_api_client.py  # APIクライアント（リクエスト送信用）
```

### 1. サーバーの起動

```bash
cd src/uv_agent_api
uvicorn uv_api_main:app --reload --port 8001
```

### 2. クライアントからの利用例

別ターミナルで：

```bash
cd src/uv_agent_api
python uv_api_client.py
```

- 対話形式でAIエージェントに質問できます。
- `quit` または `exit` で終了します。

### 3. エンドポイント一覧

- `POST /ask` : 質問を送信し、AIエージェントの応答を取得
- `GET /history` : 会話履歴を取得
- `DELETE /history` : 会話履歴をクリア

### 4. 補足
- `uv_api_agent.py` … LangGraph/LLM/Tool/会話履歴の定義とエージェント本体
- `uv_api_main.py` … FastAPIサーバーのエンドポイント定義
- `uv_api_client.py` … サーバーへリクエストを送るクライアント

APIキーや外部サービス連携が必要な場合は、各スクリプト内のコメントや環境変数設定を参照してください。

---
