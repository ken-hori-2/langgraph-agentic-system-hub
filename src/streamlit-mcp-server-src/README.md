# 🚀 MCP Tool Utilization Agent System

> **次世代AIエージェントシステム** - MCP（Model Context Protocol）ツールを活用した高度な対話型AIアプリケーション

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-green.svg)](https://streamlit.io)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-red.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--5--sonnet-teal.svg)](https://anthropic.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--7--sonnet-indigo.svg)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目次

- [概要](#概要)
- [🎮 デモ](#-デモ)
- [アプリケーション構成](#アプリケーション構成)
- [🚀 クイックスタート](#-クイックスタート)
- [📱 アプリケーション詳細](#-アプリケーション詳細)
- [🔧 セットアップ](#-セットアップ)
- [🎮 使用方法](#-使用方法)
- [🛠️ MCPツール統合](#️-mcpツール統合)
- [🔌 API統合](#-api統合)
- [🎨 カスタマイズ](#-カスタマイズ)
- [🔧 トラブルシューティング](#-トラブルシューティング)
- [📊 システム情報](#-システム情報)
- [🤝 コントリビューション](#-コントリビューション)

## 🎯 概要

このシステムは、MCP（Model Context Protocol）ツールを統合した2つの高度なAIエージェントアプリケーションを提供します。

### 🌟 主な特徴

- **🤖 多モデル対応**: OpenAI GPT-4o、Anthropic Claude-3シリーズ対応
- **🔧 動的ツール追加**: JSON設定によるMCPツールの動的追加
- **⚡ リアルタイム処理**: 非同期処理による高速レスポンス
- **🎨 モダンUI**: Streamlitによる美しいインターフェース
- **🔒 認証システム**: オプションのログイン機能
- **📊 詳細ログ**: ツール呼び出しの可視化

## 🎮 デモ

### 🎯 統合システムデモ

全機能を統合した包括的なデモンストレーション：

![Full System Demo](docs/demo.gif)

### 💬 MCPチャットアプリケーション

ReActエージェントによる対話型チャットシステム：

![MCP Chat Demo](docs/demo_chat.gif)

## 📱 アプリケーション構成

### 1. 🎵 **MCP Chat** (`mcp_chat/main.py`)
**純粋なMCPツール統合チャットエージェント**

```
mcp_chat/
├── main.py          # メインアプリケーション
├── config.json      # MCPツール設定
├── utils.py         # ユーティリティ関数
└── tools/           # カスタムツール
```

**特徴:**
- 🧠 **純粋なAIエージェント**: MCPツールのみを使用した対話型AI
- 🔧 **動的ツール管理**: リアルタイムでツールの追加・削除
- 📝 **会話履歴**: セッション管理と履歴保存
- 🎯 **専門的応答**: ツールベースの正確な情報提供

### 2. 🎵🍽️ **MCP Integration** (`mcp_integration/app_integrated_main.py`)
**音楽・レストラン検索統合システム**

```
mcp_integration/
├── app_integrated_main.py  # メインアプリケーション
├── config.json            # MCPツール設定
├── requirements_app_integrated.txt  # 依存関係
└── tools/                 # カスタムツール
```

**特徴:**
- 🎵 **Spotify統合**: 楽曲・アーティスト検索 + 埋め込みプレイヤー
- 🍽️ **レストラン検索**: HotPepper + Google Maps統合検索
- 💬 **チャットエージェント**: MCPツールを活用した対話型AI
- 🗺️ **地図表示**: Googleマップ埋め込み
- 📊 **統計情報**: 検索結果の詳細分析

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd langgraph-agentic-system-hub/src/streamlit-mcp-server-src

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r mcp_integration/requirements_app_integrated.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成：

```env
# OpenAI API (GPT-4o, GPT-4o-mini用)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API (Claude-3シリーズ用)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Spotify API
SPOTIFY_USER_ID=your_spotify_user_id
SPOTIFY_TOKEN=your_spotify_token

# HotPepper Gourmet API
HOTPEPPER_API_KEY=your_hotpepper_api_key

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# 認証設定（オプション）
USE_LOGIN=false
USER_ID=admin
USER_PASSWORD=password
```

### 3. アプリケーション起動

#### 🎵 MCP Chat（純粋なチャットエージェント）
```bash
cd mcp_chat
streamlit run main.py
```

#### 🎵🍽️ MCP Integration（統合システム）
```bash
cd mcp_integration
streamlit run app_integrated_main.py
```

## 📱 アプリケーション詳細

### 🎵 MCP Chat - 純粋なAIエージェント

**用途**: 一般的な質問応答、情報検索、タスク実行

**主な機能:**
- 🔍 **Web検索**: Tavily検索による最新情報取得
- ⏰ **時刻取得**: 現在時刻の取得
- 🎵 **音楽検索**: Spotify API統合
- 🗺️ **地図検索**: Google Maps統合
- 📚 **文書検索**: RAG（Retrieval-Augmented Generation）

**使用例:**
```
ユーザー: "東京の天気を教えて"
AI: Web検索ツールを使用して最新の天気情報を取得し、詳細を回答

ユーザー: "現在時刻は？"
AI: 時刻取得ツールを使用して正確な時刻を回答

ユーザー: "YOASOBIの曲を教えて"
AI: Spotify検索ツールを使用して楽曲情報を取得し、詳細を回答
```

### 🎵🍽️ MCP Integration - 統合検索システム

**用途**: 音楽検索、レストラン検索、統合チャット

**主な機能:**

#### 🎵 音楽検索タブ
- **Spotify API統合**: 楽曲・アーティスト・アルバム検索
- **埋め込みプレイヤー**: 直接再生可能なSpotifyプレイヤー
- **統計情報**: 人気度・再生時間・アーティスト数
- **詳細情報**: アルバム・リリース日・人気度

#### 🍽️ レストラン検索タブ
- **統合検索**: HotPepper + Google Maps
- **詳細情報**: 評価・価格・住所・ジャンル
- **地図表示**: Googleマップ埋め込み
- **リンク統合**: 予約・詳細ページへの直接リンク

#### 💬 チャットエージェントタブ
- **MCPツール統合**: 動的に追加可能なツール
- **ストリーミング応答**: リアルタイムレスポンス
- **ツール呼び出し可視化**: 実行過程の詳細表示
- **会話履歴**: セッション管理

## 🔧 セットアップ

### 必要なAPIキーの取得

#### 1. OpenAI API
1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. APIキーを生成
3. `.env`ファイルに`OPENAI_API_KEY`として設定

#### 2. Anthropic API
1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. APIキーを生成
3. `.env`ファイルに`ANTHROPIC_API_KEY`として設定

#### 3. Spotify API
1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)にアクセス
2. アプリケーションを作成
3. Client IDとClient Secretを取得
4. `.env`ファイルに設定

#### 4. HotPepper API
1. [HotPepper Web Service](https://webservice.recruit.co.jp/)にアクセス
2. APIキーを取得
3. `.env`ファイルに`HOTPEPPER_API_KEY`として設定

#### 5. Google Maps API
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. Places APIを有効化
3. APIキーを生成
4. `.env`ファイルに`GOOGLE_MAPS_API_KEY`として設定

### MCPサーバーファイルの配置

必要なMCPサーバーファイルを配置：

```bash
# 基本的なMCPサーバーファイル
mcp_server_time.py          # 時刻取得
mcp_server_search.py        # Web検索
mcp_server_spotify.py       # Spotify検索
mcp_server_hotpepper.py     # HotPepper検索
mcp_server_googlemaps.py    # Google Maps検索
mcp_server_rag.py          # 文書検索
```

## 🎮 使用方法

### 🎵 MCP Chat の使用方法

1. **アプリケーション起動**
   ```bash
   cd mcp_chat
   streamlit run main.py
   ```

2. **モデル選択**
   - サイドバーから使用するモデルを選択
   - GPT-4o、GPT-4o-mini、Claude-3シリーズから選択

3. **ツール設定**
   - 「🧰 Add MCP Tools」でツールを追加
   - JSON形式でツール設定を入力
   - 「Apply Settings」で設定を適用

4. **チャット開始**
   - 質問を入力
   - AIが適切なツールを使用して回答

### 🎵🍽️ MCP Integration の使用方法

1. **アプリケーション起動**
   ```bash
   cd mcp_integration
   streamlit run app_integrated_main.py
   ```

2. **タブ選択**
   - **🎵 Music Search**: Spotify音楽検索
   - **🍽️ Restaurant Search**: レストラン検索
   - **💬 Chat Agent**: 統合チャットエージェント

3. **音楽検索**
   - 楽曲名またはアーティスト名を入力
   - 検索結果とSpotify埋め込みプレイヤーを確認

4. **レストラン検索**
   - エリア名・ジャンル・予算を入力
   - HotPepperとGoogle Mapsの統合結果を確認

5. **チャットエージェント**
   - 自然言語で質問
   - 音楽・レストラン検索を含む統合応答

## 🛠️ MCPツール統合

### デフォルトツール

#### MCP Chat デフォルトツール
| ツール名 | 機能 | 設定 |
|---------|------|------|
| **get_current_time** | 現在時刻取得 | `mcp_server_time.py` |
| **tavily_search** | Web検索 | `mcp_server_search.py` |
| **spotify_search** | Spotify楽曲検索 | `mcp_server_spotify.py` |
| **retriever** | 文書検索 | `mcp_server_rag.py` |
| **google_maps** | 地図・場所検索 | `mcp_server_googlemaps.py` |

#### MCP Integration デフォルトツール
| ツール名 | 機能 | 設定 |
|---------|------|------|
| **spotify_search** | Spotify楽曲検索 | `mcp_server_spotify.py` |
| **hotpepper_search** | レストラン検索 | `mcp_server_hotpepper.py` |
| **google_maps** | 地図・場所検索 | `mcp_server_googlemaps.py` |
| **search** | Web検索 | `mcp_server_search.py` |

### カスタムツール追加

```json
{
  "custom_tool": {
    "command": "python",
    "args": ["./mcp_server_custom.py"],
    "transport": "stdio"
  }
}
```

### ツール設定例

```json
{
  "weather_tool": {
    "command": "python",
    "args": ["./mcp_server_weather.py"],
    "transport": "stdio"
  },
  "news_tool": {
    "url": "https://api.example.com/news",
    "transport": "sse"
  }
}
```

## 🔌 API統合

### OpenAI API (GPT-4o, GPT-4o-mini)

```python
def initialize_openai_model(model_name: str):
    """OpenAIモデルの初期化"""
    return ChatOpenAI(
        model=model_name,
        temperature=0.1,
        max_tokens=16000,  # GPT-4oシリーズのデフォルト
    )
```

### Anthropic API (Claude-3シリーズ)

```python
def initialize_anthropic_model(model_name: str):
    """Anthropicモデルの初期化"""
    max_tokens_map = {
        "claude-3-5-sonnet-latest": 8192,
        "claude-3-5-haiku-latest": 8192,
        "claude-3-7-sonnet-latest": 64000,
    }
    
    return ChatAnthropic(
        model=model_name,
        temperature=0.1,
        max_tokens=max_tokens_map.get(model_name, 8192),
    )
```

### Spotify API

```python
def search_spotify_tracks_func(query: str, limit: int = 10) -> dict:
    """Spotify楽曲検索"""
    # 認証
    auth_response = requests.post('https://accounts.spotify.com/api/token', {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    # 検索実行
    search_response = requests.get(
        f'https://api.spotify.com/v1/search?q={quote(query)}&type=track&limit={limit}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    return process_track_results(search_response.json())
```

### HotPepper API

```python
def search_hotpepper_restaurants(location: str, cuisine: str = "", budget: str = "") -> dict:
    """HotPepperレストラン検索"""
    params = {
        'key': api_key,
        'format': 'json',
        'count': 20,
        'address': location,
        'genre': cuisine,
        'budget': budget
    }
    
    response = requests.get('https://webservice.recruit.co.jp/hotpepper/gourmet/v1/', params=params)
    return process_restaurant_results(response.json())
```

### Google Maps API

```python
def search_google_maps_restaurants(location: str, cuisine: str = "", radius: int = 1000) -> dict:
    """Google Mapsレストラン検索"""
    query = f"restaurants in {location}"
    if cuisine:
        query += f" {cuisine}"
    
    params = {
        'query': query,
        'key': api_key,
        'radius': radius,
        'type': 'restaurant'
    }
    
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    return process_place_results(response.json())
```

## 🎨 カスタマイズ

### UIカスタマイズ

```python
# カスタムCSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
```

### 機能拡張

```python
# 新しい検索機能の追加
@tool
def search_weather_tool(location: str) -> str:
    """天気検索ツール"""
    return search_weather_func(location)

def search_weather_func(location: str) -> dict:
    """天気検索関数"""
    # 天気API呼び出し
    pass
```

### 設定ファイル管理

```python
# config.jsonの構造
{
  "spotify_search": {
    "command": "python",
    "args": ["./mcp_server_spotify.py"],
    "transport": "stdio"
  },
  "custom_tools": {
    "weather": {
      "command": "python",
      "args": ["./mcp_server_weather.py"],
      "transport": "stdio"
    }
  }
}
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. MCPサーバー接続エラー

```bash
# エラー: MCP server files not found
# 解決: 必要なMCPサーバーファイルを配置
ls -la mcp_server_*.py
```

#### 2. API認証エラー

```bash
# エラー: API credentials not configured
# 解決: .envファイルにAPIキーを設定
echo "OPENAI_API_KEY=your_key" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env
```

#### 3. 非同期処理エラー

```python
# Windows環境での非同期処理設定
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

#### 4. メモリ不足エラー

```python
# セッション状態のクリーンアップ
if st.button("Reset Conversation"):
    st.session_state.thread_id = random_uuid()
    st.session_state.history = []
```

#### 5. モデル選択エラー

```python
# 利用可能なモデルの確認
available_models = []
if os.environ.get("OPENAI_API_KEY"):
    available_models.extend(["gpt-4o", "gpt-4o-mini"])
if os.environ.get("ANTHROPIC_API_KEY"):
    available_models.extend(["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-7-sonnet-latest"])
```

### デバッグモード

```python
# 詳細ログの有効化
import logging
logging.basicConfig(level=logging.DEBUG)

# エラー情報の表示
try:
    result = await process_query(query, text_placeholder, tool_placeholder)
except Exception as e:
    st.error(f"エラー詳細: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
```

### パフォーマンス最適化

```python
# タイムアウト設定
st.session_state.timeout_seconds = st.slider(
    "⏱️ Response generation time limit (seconds)",
    min_value=60,
    max_value=300,
    value=120
)

# 再帰制限設定
st.session_state.recursion_limit = st.slider(
    "⏱️ Recursion call limit (count)",
    min_value=10,
    max_value=200,
    value=100
)
```

## 📊 システム情報

### 環境変数チェック

```python
# 必要なAPIキーの確認
env_vars = {
    "OpenAI API": os.getenv("OPENAI_API_KEY"),
    "Anthropic API": os.getenv("ANTHROPIC_API_KEY"),
    "Spotify API": os.getenv("SPOTIFY_USER_ID"),
    "HotPepper API": os.getenv("HOTPEPPER_API_KEY"),
    "Google Maps API": os.getenv("GOOGLE_MAPS_API_KEY")
}

for name, value in env_vars.items():
    status = "✅" if value else "❌"
    st.write(f"{status} {name}")
```

### ツール統計

```python
# 利用可能なツール数
st.write(f"🛠️ MCP Tools Count: {st.session_state.get('tool_count', 'Initializing...')}")
st.write(f"🧠 Current Model: {st.session_state.selected_model}")
```

## 🚀 高度な機能

### 認証システム

```python
# ログイン機能の有効化
use_login = os.environ.get("USE_LOGIN", "false").lower() == "true"

if use_login and not st.session_state.authenticated:
    # ログイン画面表示
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
```

### ストリーミング応答

```python
def get_streaming_callback(text_placeholder, tool_placeholder):
    """ストリーミングコールバック関数"""
    accumulated_text = []
    accumulated_tool = []

    def callback_func(message: dict):
        # リアルタイム応答処理
        pass

    return callback_func, accumulated_text, accumulated_tool
```

### 会話履歴管理

```python
# 会話履歴の保存
st.session_state.history.append({"role": "user", "content": user_query})
st.session_state.history.append({"role": "assistant", "content": final_text})

# ツール呼び出し情報の保存
if final_tool.strip():
    st.session_state.history.append({"role": "assistant_tool", "content": final_tool})
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📝 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 📞 サポート

問題や質問がある場合は、[Issues](../../issues)で報告してください。

## 👨‍💻 作者

**ken-hori-2** - [GitHub](https://github.com/ken-hori-2) - [Project Page](https://ken-hori-2.github.io/langgraph-agentic-system-hub/portfolio/)

---

**⭐ このプロジェクトが役に立ったら、スターを付けてください！** 