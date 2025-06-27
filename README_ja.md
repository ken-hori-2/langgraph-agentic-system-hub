# LangGraph Agentic System Hub

🧠 LangGraphとMCPツールを使用したマルチエージェントLLMアプリケーション構築のためのモジュラーで拡張可能なフレームワーク

---

## 🔥 概要

このプロジェクトは、**MCP（Modular Command Protocol）**を介して様々なツール（天気、Spotify、Google Mapsなど）を統合する**LangGraphベースのエージェントアーキテクチャ**を提供し、インテリジェントで動的なタスク実行を可能にします。

このリポジトリには**3つの主要コンポーネント**が含まれています：

1. **🎯 Simple ReAct Agent** (`simple-agent-mcp/`)
   - MCPツールを統合する単一のReActエージェント
   - Spotify、Web検索、時刻取得などの基本機能
   - コマンドラインインターフェース

2. **🌐 Streamlit MCP Server Interface** (`streamlit-mcp-server-src/`)
   - ReActエージェントを備えたユーザーフレンドリーなWebインターフェース
   - 動的なMCPツール管理
   - リアルタイムストリーミングレスポンス

3. **🔌 FastAPI Multi-Agent Extensible API** (`uv-agent-api/`)
   - LangGraph StateGraphベースのエージェントシステム
   - RESTful APIアクセスを備えたマルチエージェントシステムの拡張可能なアーキテクチャ

以下の機能をサポートするように設計されています：
- 🗺️ Web検索とマップツールを使用した週末スポット計画
- 🍻 空き状況チェック付きのパーティ会場検索（HotPepper、食べログ）
- 🎧 リクエストに基づくSpotify音楽検索と再生
- ✅ カレンダーとToDoツールを使用したタスク管理
- 🎯 タスクを最適なエージェントにルーティングする統合オーケストレーター

---

## 🏗️ プロジェクト構造

```txt
langgraph-agentic-system-hub/
├── README.md
├── requirements.txt
├── main.py
│
├── src/
│   ├── simple-agent-mcp/                # シンプルなAgent + MCP構成
│   │   ├── planner_agent.py             # メインエージェント
│   │   └── tools/                       # MCPサーバー群
│   │       ├── mcp_server_time.py
│   │       ├── mcp_server_search.py
│   │       └── mcp_server_spotify.py
│   │
│   ├── streamlit-mcp-server-src/        # StreamlitベースのMCPサーバーUI
│   │   ├── app_onlygpt_ken.py
│   │   ├── mcp_server_time.py
│   │   ├── mcp_server_search.py
│   │   ├── mcp_server_spotify.py
│   │   ├── mcp_server_googlemaps.py
│   │   ├── mcp_server_rag.py
│   │   ├── config.json
│   │   └── utils.py
│   │
│   └── uv-agent-api/                    # FastAPIベースのエージェントAPI
│       ├── uv_api_agent.py
│       ├── uv_api_main.py
│       └── uv_api_client.py
│
└── docs/
    └── architecture.png
```

---

## 🔧 必要条件

```txt
# LangChain関連
langchain==0.3.13
langchain-community==0.3.13
langchain-core==0.3.40
langchain-google-community==2.0.3
langchain-google-genai==2.0.11
langchain-openai==0.2.6
langchain-text-splitters==0.3.4
langgraph==0.2.45

# LLM関連
openai==1.54.3
anthropic==0.52.1
google-ai-generativelanguage==0.6.16

# データ処理・分析
pandas==2.2.3
numpy==1.26.4
scikit-learn==1.6.1
scipy==1.15.2

# Web関連
fastapi==0.115.11
uvicorn==0.34.0
streamlit==1.45.1
flask==3.1.0
flask-cors==5.0.1

# ユーティリティ
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.7.0
tqdm==4.67.0
```

以下のコマンドで依存関係を一度にインストールできます：
```bash
pip install -r requirements.txt
```

---

## 🚀 はじめに

### 1. クローンと依存関係のインストール

```bash
git clone https://github.com/kenji/langgraph-agentic-system-hub.git
cd langgraph-agentic-system-hub
pip install -r requirements.txt
```

### 2. 環境設定

ルートディレクトリに以下の変数を含む`.env`ファイルを作成してください：

```bash
# ===== LLM API Keys =====
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ===== Tool API Keys =====
# Tavily Search API (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# Spotify API (for music search)
SPOTIFY_USER_ID=your_spotify_user_id_here
SPOTIFY_TOKEN=your_spotify_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Google Maps API (for location services)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Google Search API (for web search in uv-agent-api)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here

# ===== Optional Settings =====
# Authentication (for Streamlit interface)
USE_LOGIN=true
USER_ID=your_username
USER_PASSWORD=your_password
```

#### API Keysの取得方法

1. **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Anthropic API Key**: [Anthropic Console](https://console.anthropic.com/)
3. **Tavily API Key**: [Tavily](https://tavily.com/)
4. **Spotify API**: [Spotify Developer Dashboard](https://developer.spotify.com/)
5. **Google Maps API**: [Google Cloud Console](https://console.cloud.google.com/)
6. **Google Search API**: [Google Custom Search](https://developers.google.com/custom-search)

### 3. 利用可能なツール

#### 🗺️ Google Maps API
- ルート検索とナビゲーション
- 評価と営業時間付きの場所検索
- ジオコーディング（住所から座標）
- 逆ジオコーディング（座標から住所）

#### 🔍 Web検索
- Tavily APIを使用した高度なWeb検索
- 設定可能な検索深度
- URL付きの豊富な検索結果

#### 🎵 Spotify検索
- 音楽検索とレコメンデーション
- アーティストとアルバム情報
- トラック詳細とオーディオ機能

#### ⏰ 時刻サービス
- 任意のタイムゾーンの現在時刻
- タイムゾーン変換
- フォーマットされた時刻出力

#### 📚 RAG（Retrieval-Augmented Generation）
- ドキュメントベースの質問応答
- PDFドキュメント処理
- コンテキストを考慮したレスポンス

### 4. コンポーネントの選択

このリポジトリは3つの独立した実装を提供します：

---

## 🎯 コンポーネント1: Simple ReAct Agent

### 概要

**Simple ReAct Agent**は、MCPツールを統合する単一のReActエージェントです。LangGraphの`create_react_agent`を使用して、Spotify、Web検索、時刻取得などの基本機能を提供します。

### クイックスタート

#### 1. MCPツールサーバーの実行

必要なMCPサーバーを起動します：

```bash
# Terminal 1: Spotify MCP Server
python src/simple-agent-mcp/tools/mcp_server_spotify.py

# Terminal 2: Search MCP Server
python src/simple-agent-mcp/tools/mcp_server_search.py

# Terminal 3: Time MCP Server
python src/simple-agent-mcp/tools/mcp_server_time.py
```

#### 2. エージェントの起動

```bash
python src/simple-agent-mcp/planner_agent.py
```

### 機能

- **MCPツール統合**: 複数のMCPサーバーとの統合
- **ReAct推論**: ツール使用と推論の組み合わせ
- **シンプルなインタラクション**: コマンドラインを介した直接的な会話
- **基本機能**: 音楽検索、Web検索、時刻取得

### ユースケース

- MCPツール統合の基本理解
- シンプルなAIアシスタントの構築
- CLIベースの自動化
- プロトタイプ開発

---

## 🌐 コンポーネント2: Streamlit MCP Server Interface

### 概要

**Streamlit MCP Server Interface**は、ReActエージェントを介してMCPツールと対話するためのユーザーフレンドリーなWebベースインターフェースを提供します。グラフィカルインターフェースを好み、複数のツールを簡単に管理したいユーザーに最適です。

### クイックスタート

```bash
cd src/streamlit-mcp-server-src
streamlit run app_onlygpt_ken.py
```

### 機能

- 🎯 **ReActエージェント**: 複数のツールを使用して質問に答えるインテリジェントエージェント
- 🔧 **動的ツール管理**: Webインターフェースを介したMCPツールの追加と設定
- 🗺️ **Google Maps統合**: ルート検索、場所検索、ジオコーディング、逆ジオコーディング
- 🔍 **Web検索**: Tavily検索APIを搭載
- 🎵 **Spotify統合**: 音楽検索とレコメンデーション
- ⏰ **時刻サービス**: 異なるタイムゾーンの現在時刻
- 📚 **RAGサポート**: ドキュメントベースの質問応答
- 🔐 **オプション認証**: セキュアアクセスのためのログインシステム
- 💬 **リアルタイムストリーミング**: ツール呼び出し情報付きのライブレスポンスストリーミング

### 高度な機能

#### 認証システム

`.env`で`USE_LOGIN=true`を設定してログイン保護を有効にします：

```bash
USE_LOGIN=true
USER_ID=your_username
USER_PASSWORD=your_password
```

#### モデル選択

複数のLLMモデルから選択：
- **Anthropic**: Claude 3.7 Sonnet、Claude 3.5 Sonnet、Claude 3.5 Haiku
- **OpenAI**: GPT-4o、GPT-4o Mini

#### レスポンス設定

- **タイムアウト**: レスポンス生成時間制限の調整（60-300秒）
- **再帰制限**: ツール呼び出し再帰深度の制御（10-200）
- **会話メモリ**: 自動会話履歴管理

### ユースケース

- インタラクティブなWebベースAIアシスタンス
- ツール探索と実験
- 非技術ユーザー向けのユーザーフレンドリーなAIインターフェース
- 視覚的フィードバック付きのリアルタイムAIインタラクション

---

## 🔌 コンポーネント3: FastAPI Multi-Agent Extensible API

### 概要

**FastAPI Multi-Agent Extensible API**は、LangGraph StateGraphベースのエージェントシステムです。現在は単一エージェントとして実装されていますが、将来的にマルチエージェントシステムに拡張可能なアーキテクチャを備えています。

### クイックスタート

#### 1. サーバーの起動

```bash
cd src/uv-agent-api
uvicorn uv_api_main:app --reload --port 8001
```

#### 2. クライアントの使用

別のターミナルで：

```bash
cd src/uv-agent-api
python uv_api_client.py
```

### APIエンドポイント

- `POST /ask` : 質問を送信してAIエージェントのレスポンスを取得
- `GET /history` : 会話履歴を取得
- `DELETE /history` : 会話履歴をクリア

### 統合例

```python
import requests

# エージェントに質問を送信
response = requests.post("http://localhost:8001/ask", 
                        json={"question": "What's the weather like in Tokyo?"})
result = response.json()
print(result["response"])

# 会話履歴を取得
history = requests.get("http://localhost:8001/history")
print(history.json())
```

### 機能

- **StateGraphベース**: LangGraphによる状態管理
- **RESTful API**: 標準HTTPエンドポイント
- **プログラムアクセス**: 既存アプリケーションとの簡単な統合
- **会話管理**: 組み込み会話履歴と状態管理
- **スケーラブルアーキテクチャ**: より良いパフォーマンスのためのクライアント-サーバー分離

### マルチエージェント拡張性

現在は単一エージェントとして実装されていますが、以下の理由でマルチエージェントシステムに拡張できます：

- **StateGraphアーキテクチャ**: 複数のノードとエッジを追加する機能
- **状態管理**: `AgentState`による柔軟な状態管理
- **モジュラー設計**: 新しいエージェントノードの簡単な追加

### ユースケース

- 既存Webアプリケーションとの統合
- モバイルアプリバックエンド
- 自動化ワークフローとスクリプト
- カスタムAIインターフェース
- マイクロサービスアーキテクチャ
- マルチエージェントシステムの基盤

---

## 🔄 コンポーネント比較

| 機能 | Simple ReAct Agent | Streamlit Interface | FastAPI Multi-Agent API |
|------|-------------------|-------------------|------------------------|
| **ユーザーインターフェース** | コマンドライン | Web UI | REST API |
| **複雑さ** | 低（単一ReAct） | 中（ReAct） | 高（StateGraph） |
| **ユースケース** | 基本機能 | インタラクティブ使用 | 統合と拡張 |
| **セットアップ** | 複数サーバー | 単一アプリ | クライアント-サーバー |
| **スケーラビリティ** | 低 | 中 | 高 |
| **学習曲線** | 緩やか | 緩やか | 急 |
| **マルチエージェントサポート** | なし | なし | 拡張可能 |

---

## 🧩 エージェントワークフロー例

```txt
ユーザー: "週末に行く場所を見つけて"
→ オーケストレーター: "PlannerAgent"にルーティング
→ PlannerAgent: Web検索MCPを使用
→ Google Maps MCP + HotPepper MCPから情報を取得
→ LangGraphを介してユーザーに結果を返す
```

## 🔮 今後の計画

- 🧠 LangChainメモリとの統合
- 🔍 動的検索のためのRAG（Retrieval-Augmented Generation）
- 📆 自動スケジューリングのためのGoogle Calendar統合
- 📎 Notion自動要約機能
- 🎤 YouTube音声分離ツールとの統合
- 💬 各エージェントのプロンプト最適化
- 🗺️ LangGraph SDKによる視覚的ワークフロー生成

## ✨ 使用例

| 使用例 | 説明 |
|--------|------|
| 🎵 音楽検索 | ユーザーのリクエストに基づいてSpotifyから曲を検索・レコメンド |
| 🍺 パーティ会場検索 | 人数、日付、エリアに基づいて良い会場を見つけて空き状況をチェック |
| 🌤 天気情報 | 現在または指定された場所の天気情報を取得してアドバイスを提供 |
| 📆 タスク管理 | Google Calendar統合によるスケジュールとToDoリストの管理 |
| 📍 お出かけアイデア | 人気の週末スポットを提案してレビューを取得 |
| 🗺️ ルート計画 | Google Maps APIを使用した詳細な方向とルート情報の取得 |
| 🔍 Web調査 | 情報収集のための包括的なWeb検索の実行 |

## 👤 作者

**Centaurus-Ken（[@ken-hori-2](https://github.com/ken-hori-2)）**

LangGraph × MCPを使用したエージェントAIシステムの実験を行う開発者。  
アイデア創出からデモ開発、プレゼンテーションまで、音楽、天気、パーティ計画、スケジュール管理などの実世界のユースケースに焦点を当てています。  
エッジAIモデル設計、デモ開発、CI/CDパイプライン自動化の経験もあります。

## 📄 ライセンス

MIT License.

モジュラーツールオーケストレーションによる次世代LLMアプリケーションの探索のためにCentaurus-Kenによって作成されました。

---