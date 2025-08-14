# 🤖 LangGraph Multi-Agent Supervisor System (CLI)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://langchain-ai.github.io/langgraph/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--5--sonnet-teal.svg)](https://anthropic.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--7--sonnet-indigo.svg)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🚀 日本語対応のマルチエージェントAIシステム** - スケジュール管理、音楽検索、レストラン検索、旅行プランニングなどを専門エージェントが協調して処理

[English](#english) | [日本語](#japanese)

</div>

---

## 📋 目次

- [🎯 概要](#-概要)
- [🌟 主な特徴](#-主な特徴)
- [🏗️ アーキテクチャ](#️-アーキテクチャ)
- [🚀 機能一覧](#-機能一覧)
- [⚙️ セットアップ](#️-セットアップ)
- [🎮 使用方法](#-使用方法)
- [🤖 エージェント詳細](#-エージェント詳細)
- [🔌 API統合](#-api統合)
- [📊 Streamlit統合](#-streamlit統合)
- [🔧 トラブルシューティング](#-トラブルシューティング)
- [📝 ライセンス](#-ライセンス)

---

## 🎯 概要

このシステムは、LangGraphを使用したマルチエージェントAIシステムです。各専門エージェントが協調して、ユーザーの様々なリクエストを効率的に処理します。

## 🌟 主な特徴

<div align="center">

| 🤖 **7つの専門エージェント** | 🔄 **リアルタイムAPI統合** | 🇯🇵 **日本語完全対応** |
|------------------------------|---------------------------|----------------------|
| 各分野の専門知識を持つAIエージェント | Spotify、Google Maps、ホットペッパーグルメなど | 自然な日本語での対話が可能 |

| 📊 **可視化機能** | 📅 **スケジュール管理** | 🎨 **多様なインターフェース** |
|-------------------|------------------------|------------------------------|
| Streamlitによる美しいデータ可視化 | Googleカレンダーとの連携 | CLI・GUI・API対応 |

</div>

## 🏗️ アーキテクチャ

### システム構成図

<details>
<summary>📊 アーキテクチャ詳細（クリックして展開）</summary>

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Multi-Agent Supervisor System Architecture</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .architecture {
            padding: 40px;
        }
        .layer {
            margin-bottom: 40px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
        }
        .layer-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 2px solid #e1e5e9;
            font-weight: bold;
            font-size: 1.1em;
            color: #495057;
        }
        .layer-content {
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .component {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .component:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .component-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .component h3 {
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 1.1em;
        }
        .component p {
            margin: 0;
            color: #6c757d;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .flow-arrow {
            text-align: center;
            font-size: 2em;
            color: #667eea;
            margin: 20px 0;
        }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .agent {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            font-size: 0.9em;
        }
        .agent-icon {
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        .api-section {
            background: #e3f2fd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .api-item {
            background: white;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            border: 1px solid #bbdefb;
        }
        .api-icon {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        .features {
            background: #f3e5f5;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .feature-item {
            background: white;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            border: 1px solid #e1bee7;
        }
        .feature-icon {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        @media (max-width: 768px) {
            .layer-content {
                grid-template-columns: 1fr;
            }
            .agent-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .api-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .feature-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LangGraph Multi-Agent Supervisor System</h1>
            <p>7つの専門エージェントが協調して複雑なタスクを処理する統合システム</p>
        </div>
        
        <div class="architecture">
            <!-- User Interface Layer -->
            <div class="layer">
                <div class="layer-header">💻 ユーザーインターフェース層</div>
                <div class="layer-content">
                    <div class="component">
                        <div class="component-icon">🖥️</div>
                        <h3>CLI Interface</h3>
                        <p>コマンドライン操作・スクリプト実行・バッチ処理</p>
                    </div>
                    <div class="component">
                        <div class="component-icon">🌐</div>
                        <h3>GUI Interface</h3>
                        <p>StreamlitベースのWebインターフェース・リアルタイム可視化</p>
                    </div>
                    <div class="component">
                        <div class="component-icon">🔧</div>
                        <h3>MCP Integration</h3>
                        <p>動的ツール追加・プロトコル統合・拡張性</p>
                    </div>
                </div>
            </div>

            <div class="flow-arrow">⬇️</div>

            <!-- Supervisor Layer -->
            <div class="layer">
                <div class="layer-header">🎯 スーパーバイザー層</div>
                <div class="layer-content">
                    <div class="component">
                        <div class="component-icon">🧠</div>
                        <h3>Task Router</h3>
                        <p>リクエスト解析・エージェント選択・優先度管理</p>
                    </div>
                    <div class="component">
                        <div class="component-icon">⚙️</div>
                        <h3>Agent Pool</h3>
                        <p>7つの専門エージェント・負荷分散・フェイルオーバー</p>
                    </div>
                    <div class="component">
                        <div class="component-icon">📊</div>
                        <h3>Result Coordinator</h3>
                        <p>レスポンス統合・品質保証・フォーマット標準化</p>
                    </div>
                </div>
            </div>

            <div class="flow-arrow">⬇️</div>

            <!-- Agent Layer -->
            <div class="layer">
                <div class="layer-header">🤖 エージェント層</div>
                <div class="agent-grid">
                    <div class="agent">
                        <div class="agent-icon">📅</div>
                        <div>Scheduler Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">スケジュール管理</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🎵</div>
                        <div>Music Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">音楽検索</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🍽️</div>
                        <div>Restaurant Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">レストラン検索</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🎬</div>
                        <div>Video Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">動画検索</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🏨</div>
                        <div>Travel Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">旅行プランニング</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🔢</div>
                        <div>Math Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">数学計算</div>
                    </div>
                    <div class="agent">
                        <div class="agent-icon">🔍</div>
                        <div>Research Agent</div>
                        <div style="font-size: 0.8em; opacity: 0.9;">情報収集</div>
                    </div>
                </div>
            </div>

            <div class="flow-arrow">⬇️</div>

            <!-- API Layer -->
            <div class="layer">
                <div class="layer-header">🔌 外部API・サービス層</div>
                <div class="api-section">
                    <div class="api-grid">
                        <div class="api-item">
                            <div class="api-icon">🎵</div>
                            <div>Spotify API</div>
                            <div style="font-size: 0.8em; color: #666;">音楽・プレイリスト</div>
                        </div>
                        <div class="api-item">
                            <div class="api-icon">🗺️</div>
                            <div>Google Maps API</div>
                            <div style="font-size: 0.8em; color: #666;">地図・場所検索</div>
                        </div>
                        <div class="api-item">
                            <div class="api-icon">📅</div>
                            <div>Google Calendar API</div>
                            <div style="font-size: 0.8em; color: #666;">スケジュール管理</div>
                        </div>
                        <div class="api-item">
                            <div class="api-icon">🍽️</div>
                            <div>HotPepper API</div>
                            <div style="font-size: 0.8em; color: #666;">レストラン検索</div>
                        </div>
                        <div class="api-item">
                            <div class="api-icon">🎬</div>
                            <div>YouTube API</div>
                            <div style="font-size: 0.8em; color: #666;">動画検索</div>
                        </div>
                        <div class="api-item">
                            <div class="api-icon">🔍</div>
                            <div>Tavily Search API</div>
                            <div style="font-size: 0.8em; color: #666;">Web検索</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Features Section -->
            <div class="features">
                <h3 style="margin: 0 0 15px 0; color: #7b1fa2;">✨ 主要機能</h3>
                <div class="feature-list">
                    <div class="feature-item">
                        <div class="feature-icon">🤖</div>
                        <div>マルチエージェント</div>
                        <div style="font-size: 0.8em; color: #666;">7つの専門エージェント</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🎯</div>
                        <div>自動振り分け</div>
                        <div style="font-size: 0.8em; color: #666;">最適エージェント選択</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">💻</div>
                        <div>多様なインターフェース</div>
                        <div style="font-size: 0.8em; color: #666;">CLI・GUI・API</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🤖</div>
                        <div>多モデル対応</div>
                        <div style="font-size: 0.8em; color: #666;">GPT-4o・Claude-3</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🔄</div>
                        <div>協調処理</div>
                        <div style="font-size: 0.8em; color: #666;">エージェント間連携</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <div>結果統合</div>
                        <div style="font-size: 0.8em; color: #666;">統合レスポンス</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

</details>

### ワークフロー図

![Multi-Agent Workflow](../assets/workflow.png)

**ワークフロー説明:**
- **スーパーバイザー**: 中央の黄色いボックスで、全体のプロセスを調整
- **7つの専門エージェント**: 下部の黄色いボックスで、各分野に特化
- **ツール連携**: 各エージェントが専用ツールを使用してタスクを実行
- **制御フロー**: スーパーバイザーが適切なエージェントを選択・実行

## 🚀 機能一覧

<div align="center">

| エージェント | 機能 | 対応API |
|-------------|------|---------|
| 📅 **Scheduler Agent** | スケジュール管理・Googleカレンダー連携 | Google Calendar API |
| 🎵 **Music Agent** | 楽曲・アーティスト・プレイリスト検索 | Spotify API |
| 🎬 **Video Agent** | YouTube動画検索・情報取得 | YouTube Data API |
| 🏨 **Travel Agent** | ホテル・宿泊施設検索 | じゃらん・Airbnb |
| 🍽️ **Restaurant Agent** | レストラン検索・予約確認 | ホットペッパーグルメ・Google Places |
| 🔢 **Math Agent** | 数学計算 | - |
| 🔍 **Research Agent** | Web検索・情報収集 | Tavily Search |

</div>

## ⚙️ セットアップ

### 1️⃣ 環境要件

```bash
Python 3.8+
```

### 2️⃣ 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3️⃣ 環境変数の設定

`.env`ファイルを作成し、以下のAPIキーを設定してください：

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
GOOGLE_CALENDAR_ID=your_calendar_id

# Spotify
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_USER_ID=your_spotify_user_id
SPOTIFY_TOKEN=your_spotify_token

# HotPepper Gourmet
RECRUIT_API_KEY=your_recruit_api_key

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key

# Tavily Search
TAVILY_API_KEY=your_tavily_api_key
```

### 4️⃣ Googleカレンダー認証設定

```bash
# credentials.jsonファイルを配置
# 初回実行時にOAuth2認証が実行されます
```

## 🎮 使用方法

### 📱 基本的な使用方法

```python
from supervisor_workers_multiagents import app

# ユーザーリクエストの実行
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "明日の15時に会議を予定に入れて"
        }
    ]
})

print(result["messages"][-1]["content"])
```

### 🌐 Streamlitアプリケーション

```python
import streamlit as st
from supervisor_workers_multiagents import run_agent

st.title("🤖 AI アシスタント")

user_input = st.text_input("何かお手伝いできることはありますか？")

if user_input:
    result = run_agent([{"role": "user", "content": user_input}])
    st.write(result["text"])
```

## 🤖 エージェント詳細

### 📅 Scheduler Agent (スケジューラー)

**機能**: Googleカレンダーとの連携によるスケジュール管理

```python
# 使用例
"明日の15時に会議を予定に入れて"
"今日の14:30に歯医者の予約を入れて"
"来週月曜日の10時に面接を予定に入れて"
```

**対応ツール**:
- `add_to_google_calendar()`: カレンダーに予定追加
- `get_current_time()`: 現在時刻取得
- `calculate_target_date()`: 相対日付の計算

### 🎵 Music Agent (音楽)

**機能**: Spotify APIを使用した音楽検索・推薦

```python
# 使用例
"ビートルズの曲を探して"
"人気のプレイリストを教えて"
"アーティスト情報を教えて"
```

**対応ツール**:
- `search_spotify_tracks()`: 楽曲検索
- `get_spotify_playlist()`: プレイリスト取得
- `search_spotify_artists()`: アーティスト検索

### 🍽️ Restaurant Agent (レストラン)

**機能**: レストラン検索・予約・地図連携

```python
# 使用例
"渋谷のイタリアンを探して"
"新宿の3000円以下のレストランを探して"
"このレストランの場所を教えて"
```

**対応ツール**:
- `search_hotpepper_restaurants()`: ホットペッパーグルメ検索
- `search_google_maps_restaurants()`: Google Maps検索
- `generate_google_maps_url()`: 地図URL生成
- `generate_directions_url()`: 経路案内URL生成

### 🏨 Travel Agent (旅行)

**機能**: ホテル・宿泊施設の検索・予約

```python
# 使用例
"東京のホテルを明日から2泊で探して"
"大阪のAirbnbを来週から3泊で探して"
```

**対応ツール**:
- `search_jalan_hotels()`: じゃらんホテル検索
- `search_airbnb_accommodations()`: Airbnb検索

### 🎬 Video Agent (動画)

**機能**: YouTube動画検索・情報取得

```python
# 使用例
"料理の動画を探して"
"この動画の詳細を教えて"
```

**対応ツール**:
- `search_youtube_videos()`: YouTube動画検索
- `get_video_info()`: 動画詳細情報取得

## 🔌 API統合

### Spotify API

```python
# 楽曲検索
result = search_spotify_tracks("ビートルズ")
print(result["results"])

# アーティスト検索
result = search_spotify_artists("ビートルズ")
print(result["results"])
```

### ホットペッパーグルメAPI

```python
# レストラン検索
result = search_hotpepper_restaurants(
    location="渋谷",
    cuisine="イタリアン",
    budget="3000円以下"
)
print(result["restaurants"])
```

### Google Maps API

```python
# 地図URL生成
result = generate_google_maps_url("東京都渋谷区1-1-1", "レストラン名")
print(result["google_maps_url"])

# 経路案内URL生成
result = generate_directions_url("東京駅", "レストラン名", "transit")
print(result["directions_url"])
```

## 📊 Streamlit統合

### 可視化機能

```python
# レストラン検索結果の可視化
visualize_restaurant_results_streamlit(restaurants)

# カテゴリ別件数グラフ
visualize_restaurant_category_count_streamlit(restaurants)

# 評価分布グラフ
visualize_restaurant_rating_streamlit(restaurants)

# Spotify埋め込みプレイヤー
show_spotify_embeds_streamlit(tracks)

# Googleマップ埋め込み
show_googlemap_embed_streamlit("東京都渋谷区1-1-1")
```

### 完全なStreamlitアプリ例

```python
import streamlit as st
from supervisor_workers_multiagents import run_agent, visualize_restaurant_results_streamlit

st.set_page_config(page_title="AI アシスタント", layout="wide")

st.title("🤖 AI マルチエージェントアシスタント")

# サイドバー
st.sidebar.header("機能選択")
agent_type = st.sidebar.selectbox(
    "エージェントタイプ",
    ["自動選択", "レストラン検索", "音楽検索", "スケジュール管理", "旅行プランニング"]
)

# メインコンテンツ
user_input = st.text_area("何かお手伝いできることはありますか？", height=100)

if st.button("送信"):
    if user_input:
        with st.spinner("AIが処理中..."):
            result = run_agent([{"role": "user", "content": user_input}])
            
        st.success("処理完了！")
        st.write(result["text"])
        
        # レストラン検索結果の可視化
        if result.get("results") and "restaurants" in str(result["results"]):
            restaurants = result["results"].get("restaurants", [])
            if restaurants:
                visualize_restaurant_results_streamlit(restaurants)
```

## 🔧 トラブルシューティング

### ❗ よくある問題

#### 1️⃣ APIキーエラー

```bash
# エラー: API認証情報が設定されていません
# 解決: .envファイルにAPIキーを正しく設定
```

#### 2️⃣ Googleカレンダー認証エラー

```bash
# エラー: credentials.jsonが見つかりません
# 解決: Google Cloud Consoleから認証ファイルをダウンロード
```

#### 3️⃣ 依存関係エラー

```bash
# エラー: ModuleNotFoundError
# 解決: pip install -r requirements.txt
```

### 🐛 デバッグモード

```python
# デバッグ情報を表示
import logging
logging.basicConfig(level=logging.DEBUG)

# 詳細なエラー情報を取得
try:
    result = app.invoke({"messages": [{"role": "user", "content": "test"}]})
except Exception as e:
    print(f"エラー詳細: {e}")
    import traceback
    traceback.print_exc()
```

## 📝 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🤝 コントリビューション

<div align="center">

1. 🍴 このリポジトリをフォーク
2. 🌿 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 💾 変更をコミット (`git commit -m 'Add amazing feature'`)
4. 📤 ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. 🔄 プルリクエストを作成

</div>

## 📞 サポート

問題や質問がある場合は、[Issues](../../issues)で報告してください。

---

**🌟 スターを付けてください！**

このプロジェクトが役に立った場合は、GitHubでスターを付けてください。

---

## English

<div align="center">

**🚀 Japanese Multi-Agent AI System** - Specialized agents collaborate to handle schedule management, music search, restaurant search, travel planning, and more

</div>

### 🌟 Main Features

<div align="center">

| 🤖 **7 Specialized Agents** | 🔄 **Real-time API Integration** | 🇯🇵 **Full Japanese Support** |
|------------------------------|----------------------------------|-------------------------------|
| AI agents with expertise in various fields | Spotify, Google Maps, HotPepper Gourmet, etc. | Natural Japanese conversation |

| 📊 **Visualization Features** | 📅 **Schedule Management** | 🎨 **Multiple Interfaces** |
|--------------------------------|----------------------------|----------------------------|
| Beautiful data visualization with Streamlit | Google Calendar integration | CLI, GUI, API support |

</div>

### 🏗️ Architecture

The system uses LangGraph to orchestrate 7 specialized agents that work together to efficiently process various user requests.

### 🚀 Feature List

<div align="center">

| Agent | Function | Supported APIs |
|-------|----------|----------------|
| 📅 **Scheduler Agent** | Schedule management & Google Calendar integration | Google Calendar API |
| 🎵 **Music Agent** | Track, artist & playlist search | Spotify API |
| 🎬 **Video Agent** | YouTube video search & information retrieval | YouTube Data API |
| 🏨 **Travel Agent** | Hotel & accommodation search | Jalan, Airbnb |
| 🍽️ **Restaurant Agent** | Restaurant search & reservation confirmation | HotPepper Gourmet, Google Places |
| 🔢 **Math Agent** | Mathematical calculations | - |
| 🔍 **Research Agent** | Web search & information gathering | Tavily Search |

</div>

### ⚙️ Setup

#### 1️⃣ Environment Requirements

```bash
Python 3.8+
```

#### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3️⃣ Environment Variables

Create a `.env` file with the following API keys:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
GOOGLE_CALENDAR_ID=your_calendar_id

# Spotify
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_USER_ID=your_spotify_user_id
SPOTIFY_TOKEN=your_spotify_token

# HotPepper Gourmet
RECRUIT_API_KEY=your_recruit_api_key

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key

# Tavily Search
TAVILY_API_KEY=your_tavily_api_key
```

#### 4️⃣ Google Calendar Authentication

```bash
# Place credentials.json file
# OAuth2 authentication will be executed on first run
```

### 🎮 Usage

#### 📱 Basic Usage

```python
from supervisor_workers_multiagents import app

# Execute user request
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Schedule a meeting for tomorrow at 3 PM"
        }
    ]
})

print(result["messages"][-1]["content"])
```

#### 🌐 Streamlit Application

```python
import streamlit as st
from supervisor_workers_multiagents import run_agent

st.title("🤖 AI Assistant")

user_input = st.text_input("How can I help you?")

if user_input:
    result = run_agent([{"role": "user", "content": user_input}])
    st.write(result["text"])
```

### 🤖 Agent Details

#### 📅 Scheduler Agent

**Function**: Schedule management with Google Calendar integration

```python
# Usage examples
"Schedule a meeting for tomorrow at 3 PM"
"Add a dentist appointment for today at 2:30 PM"
"Schedule an interview for next Monday at 10 AM"
```

#### 🎵 Music Agent

**Function**: Music search and recommendations using Spotify API

```python
# Usage examples
"Search for Beatles songs"
"Show me popular playlists"
"Tell me about artist information"
```

#### 🍽️ Restaurant Agent

**Function**: Restaurant search, reservations, and map integration

```python
# Usage examples
"Find Italian restaurants in Shibuya"
"Search for restaurants under 3000 yen in Shinjuku"
"Show me the location of this restaurant"
```

### 🔌 API Integration

#### Spotify API

```python
# Track search
result = search_spotify_tracks("Beatles")
print(result["results"])

# Artist search
result = search_spotify_artists("Beatles")
print(result["results"])
```

#### HotPepper Gourmet API

```python
# Restaurant search
result = search_hotpepper_restaurants(
    location="Shibuya",
    cuisine="Italian",
    budget="Under 3000 yen"
)
print(result["restaurants"])
```

### 🔧 Troubleshooting

#### ❗ Common Issues

1. **API Key Error**: Ensure API keys are correctly set in `.env` file
2. **Google Calendar Authentication Error**: Download authentication file from Google Cloud Console
3. **Dependency Error**: Run `pip install -r requirements.txt`

### 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

### 🤝 Contribution

<div align="center">

1. 🍴 Fork this repository
2. 🌿 Create feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to branch (`git push origin feature/amazing-feature`)
5. 🔄 Create Pull Request

</div>

### 📞 Support

For issues and questions, please report in [Issues](../../issues).

---

<div align="center">

**⭐️ Star this project!**

If this project was helpful, please give it a star on GitHub.

</div> 