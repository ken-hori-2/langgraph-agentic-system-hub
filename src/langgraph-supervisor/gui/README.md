# 🧠 Agentic AI Multi-Agent Assistant(GUI)
<!-- > **🚀 インテリジェントなマルチエージェントシステムによる多様なタスク処理** -->

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--5--sonnet-teal.svg)](https://anthropic.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--7--sonnet-indigo.svg)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🚀 インテリジェントなマルチエージェントシステムによる多様なタスク処理**

[English](#english) | [日本語](#japanese)

</div>

---

## 🎥 デモ動画

<div align="center">

**🎬 GUIマルチエージェントシステムの動作デモ**

*StreamlitベースのWebインターフェースでのマルチエージェントシステムの動作をご覧いただけます。*

---

### 📹 デモ動画1: 居酒屋検索 × 音楽推薦

![GUI Demo 1](../assets/demo_ja.gif)

*居酒屋検索と音楽推薦のプレビュー - より詳しく見るには下のボタンをクリック*

[![GUI Demo 1](https://img.shields.io/badge/🎬-デモ動画を見る-blue?style=for-the-badge&logo=youtube)](../assets/demo_ja.mp4)

*このデモでは、ユーザーが「渋谷でオシャレな居酒屋を探して、ミセスの曲を教えて」と質問すると、Restaurant AgentやMusic Agent等と協調して回答を生成します。*

---

### 📹 デモ動画2: 動画検索 × 天気情報

![GUI Demo 2](../assets/demo_en.gif)

*動画検索と天気情報のプレビュー - より詳しく見るには下のボタンをクリック*

[![GUI Demo 2](https://img.shields.io/badge/🎬-デモ動画を見る-blue?style=for-the-badge&logo=youtube)](../assets/demo_en.mp4)

*このデモでは、ユーザーが「英語の勉強用の動画コンテンツを探して、明日の天気を教えて」と質問すると、Video AgentやWeather Agent等と協調して回答を生成します。*

<!-- ---

### 🎞️ 統合システムデモ

![Full System Demo](../assets/demo.gif)

*統合システムのプレビュー - より詳しく見るには下のボタンをクリック*

[![Full System Demo](https://img.shields.io/badge/🎬-デモ動画を見る-blue?style=for-the-badge&logo=youtube)](../assets/demo.mp4)

*全機能を統合した包括的なデモンストレーションです。* -->

</div>

---

## 📋 目次

- [🌟 特徴](#-特徴)
- [🚀 クイックスタート](#-クイックスタート)
- [🎯 利用可能なエージェント](#-利用可能なエージェント)
- [🔄 システムワークフロー](#-システムワークフロー)
- [💻 使用方法](#-使用方法)
- [🛠️ 開発者向け情報](#️-開発者向け情報)
- [🔧 トラブルシューティング](#-トラブルシューティング)
- [📈 パフォーマンス](#-パフォーマンス)
- [🤝 コントリビューション](#-コントリビューション)

---

## 🌟 特徴

<div align="center">

| 🤖 **専門エージェント** | 🧠 **自動選択** | 🎨 **モダンUI** |
|------------------------|----------------|----------------|
| 音楽、動画、旅行、レストラン、スケジュール管理など、各分野の専門エージェント | ユーザーのリクエストを分析し、最適なエージェントを自動選択 | Streamlitによる美しく直感的なインターフェース |

| 📊 **リアルタイム分析** | 🔧 **柔軟な設定** | ⚡ **高速処理** |
|------------------------|------------------|----------------|
| チャット履歴と処理時間の詳細な分析 | デバッグモード、言語設定、API設定のカスタマイズ | GPT-4o、Claude 3.5/3.7による高速レスポンス |

</div>

---

## 🚀 クイックスタート

### 1️⃣ 環境セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd langgraph-agentic-system-hub/src/langgraph-supervisor/gui

# 仮想環境の作成とアクティベート
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 2️⃣ 環境変数の設定

#### 🔑 APIキーの取得方法

<div align="center">

| API | 取得方法 | リンク |
|-----|----------|--------|
| **OpenAI API** | OpenAIアカウントでAPIキーを生成 | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **Anthropic API** | AnthropicアカウントでAPIキーを生成 | [Anthropic Console](https://console.anthropic.com/) |
| **Tavily API** | Tavilyで無料アカウントを作成 | [Tavily API](https://tavily.com/) |
| **Google Custom Search** | Google Cloud ConsoleでCustom Search APIを有効化 | [Google Custom Search](https://developers.google.com/custom-search/v1/overview) |
| **Google Maps API** | Google Cloud ConsoleでMaps APIを有効化 | [Google Maps Platform](https://developers.google.com/maps/documentation/javascript/get-api-key) |
| **Hotpepper API** | リクルートWEBサービスでアカウントを作成 | [Hotpepper API](https://webservice.recruit.co.jp/doc/hotpepper/) |
| **Spotify API** | Spotify Developerでアプリを作成 | [Spotify Developer](https://developer.spotify.com/documentation/web-api) |

</div>

#### 📝 .envファイルの設定

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Tavily API
TAVILY_API_KEY=your_tavily_api_key_here

# Google Custom Search
GOOGLE_CSE_ID=your_google_cse_id_here

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Hotpepper API
HOTPEPPER_API_KEY=your_hotpepper_api_key_here

# Spotify API
SPOTIFY_USER_ID=your_spotify_user_id_here
SPOTIFY_TOKEN=your_spotify_token_here

# Optional: LangSmith
# LANGSMITH_API_KEY=your_langsmith_api_key_here
# LANGSMITH_TRACING=true
# LANGSMITH_ENDPOINT=https://api.smith.langchain.com
# LANGSMITH_PROJECT=LangGraph-MCP-Agents

# Login settings
USE_LOGIN=false
USER_ID=admin
USER_PASSWORD=admin1234
```

### 3️⃣ アプリケーションの起動

```bash
# 日本語版
streamlit run streamlit_app.py

# 英語版
streamlit run streamlit_app_en.py
```

🌐 ブラウザで `http://localhost:8501` にアクセスしてください。

---

## 🎯 利用可能なエージェント

<div align="center">

| エージェント | 機能 | 使用例 |
|-------------|------|--------|
| 🧠 **Auto Selection** | 自動エージェント選択 | 任意のリクエスト |
| 🎼 **Music Expert** | Spotify楽曲検索・プレイリスト取得 | "ビートルズの楽曲を検索" |
| 🎬 **Video Expert** | YouTube動画検索・情報取得 | "プログラミングチュートリアル動画" |
| 🗺️ **Travel Expert** | ホテル・Airbnb検索 | "東京のホテルを検索" |
| 🍽️ **Restaurant Expert** | レストラン検索・予約 | "渋谷のイタリアンレストラン" |
| 📅 **Scheduler** | Google Calendar管理 | "明日15時に会議をスケジュール" |
| 🔢 **Math Expert** | 計算・数式処理 | "複雑な数式の計算" |
| 🔬 **Research Expert** | Web検索・情報収集 | "最新のAI技術について調べて" |

</div>

---

## 🔄 システムワークフロー

<div align="center">

![Workflow](../assets/workflow.png)

**マルチエージェントシステムの処理フロー**

</div>

---

## 💻 使用方法

### 📱 基本的な使い方

<div align="center">

| ステップ | 説明 |
|---------|------|
| 1️⃣ **エージェント選択** | サイドバーから使用したいエージェントを選択 |
| 2️⃣ **リクエスト入力** | テキストエリアに質問やリクエストを入力 |
| 3️⃣ **送信** | "🚀 Send"ボタンをクリックして処理開始 |
| 4️⃣ **結果確認** | AIの回答と詳細結果を確認 |

</div>

### 🔧 高度な機能

#### 📊 分析ダッシュボード
- 📈 チャット履歴の統計情報
- ⏱️ 処理時間の分布グラフ
- 📏 メッセージ長の時系列分析

#### ⚙️ システム設定
- 🐛 **デバッグモード**: 詳細な処理情報を表示
- 🎯 **最新回答のみ表示**: 最新のAI回答のみを表示
- 🔍 **API設定確認**: 各APIキーの設定状況を確認

#### ⚡ クイックアクション
サイドバーのクイックボタンで素早くエージェントを切り替え：

<div align="center">

| 🎼 Music | 🍽️ Restaurant | 🗺️ Travel | 🎬 Video |
|----------|---------------|-----------|----------|

</div>

---

## 🛠️ 開発者向け情報

### 🏗️ アーキテクチャ

```
gui/
├── 📱 streamlit_app.py          # 日本語版メインアプリ
├── 🌍 streamlit_app_en.py       # 英語版メインアプリ
├── 🤖 supervisor_workers_multiagents.py  # エージェントシステム
├── 🐧 setup.sh                  # macOS/Linux用セットアップスクリプト
├── 🪟 setup.bat                 # Windows用セットアップスクリプト
├── 📦 requirements.txt          # 依存関係
└── 📖 README.md                 # このファイル
```
<!-- ├── ⚙️ .env                      # 環境変数設定 -->

### 🔧 主要コンポーネント

<div align="center">

| コンポーネント | 役割 |
|---------------|------|
| **LangGraph Supervisor** | エージェントのオーケストレーション |
| **Streamlit UI** | モダンなWebインターフェース |
| **Multi-Agent System** | 専門エージェントの統合 |
| **API Integration** | 各種外部APIとの連携 |
| **GPT-4o & Claude 3.5/3.7** | 高性能AIモデル |

</div>

### 🎨 カスタマイズ

#### ➕ 新しいエージェントの追加

1. `supervisor_workers_multiagents.py`に新しいエージェント関数を追加
2. ツールとプロンプトを定義
3. メインアプリにエージェント選択肢を追加

#### 🎨 UIのカスタマイズ

- 🎨 CSSスタイルの変更: `streamlit_app.py`のカスタムCSSセクション
- 📐 レイアウトの調整: Streamlitコンポーネントの配置変更
- 🌈 テーマの変更: `st.set_page_config`の設定調整

---

## 🔧 トラブルシューティング

### ❗ よくある問題

#### 🔑 APIキーエラー
```
Error: API key not found
```
**✅ 解決方法**: `.env`ファイルでAPIキーが正しく設定されているか確認

#### 📦 インポートエラー
```
Import Error: supervisor_workers_multiagents
```
**✅ 解決方法**: ファイルパスとPython環境を確認

#### ⏰ 処理タイムアウト
```
Processing timeout
```
**✅ 解決方法**: ネットワーク接続とAPI制限を確認

### 🐛 デバッグモード

サイドバーの"🐛 Debug Mode"を有効にすると、詳細な処理情報が表示されます：

- 🔍 エージェント実行結果
- 📡 API呼び出し詳細
- 📋 エラートレースバック

---

## 📈 パフォーマンス

### ⚡ 処理時間の最適化

<div align="center">

| 項目 | 詳細 |
|------|------|
| **平均処理時間** | 2-5秒 |
| **並列処理** | 複数エージェントの同時実行 |
| **キャッシュ** | 重複リクエストの効率化 |
| **高速AI** | GPT-4o、Claude 3.5/3.7による高速レスポンス |

</div>

### 📊 スケーラビリティ

- 🔄 **水平スケーリング**: 複数インスタンスでの実行
- ⚖️ **負荷分散**: エージェント間の負荷分散
- 💾 **リソース管理**: メモリとCPU使用量の最適化

---

## 🤝 コントリビューション

<div align="center">

1. 🍴 このリポジトリをフォーク
2. 🌿 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 💾 変更をコミット (`git commit -m 'Add amazing feature'`)
4. 📤 ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. 🔄 プルリクエストを作成

</div>

---

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 👨‍💻 作者

**ken-hori-2** - [GitHub](https://github.com/ken-hori-2)

## 🙏 謝辞

<div align="center">

| ライブラリ | 用途 |
|-----------|------|
| [LangGraph](https://github.com/langchain-ai/langgraph) | エージェントオーケストレーション |
| [Streamlit](https://streamlit.io/) | Webアプリケーションフレームワーク |
| [OpenAI](https://openai.com/) | GPT-4o-miniモデル |
| [Anthropic](https://anthropic.com/) | Claude 3.5/3.7モデル |

</div>

---

<div align="center">

**🌟 スターを付けてください！**

このプロジェクトが役に立った場合は、GitHubでスターを付けてください。

</div>

---

## English

<div align="center">

**🚀 Intelligent Multi-Agent System for Diverse Task Processing**

</div>

### 🌟 Features

<div align="center">

| 🤖 **Specialized Agents** | 🧠 **Auto Selection** | 🎨 **Modern UI** |
|---------------------------|----------------------|------------------|
| Music, video, travel, restaurant, scheduling, and more | Automatically analyzes user requests and selects optimal agents | Beautiful and intuitive interface powered by Streamlit |

| 📊 **Real-time Analytics** | 🔧 **Flexible Settings** | ⚡ **High Performance** |
|----------------------------|--------------------------|------------------------|
| Detailed analysis of chat history and processing times | Customizable debug mode, language settings, and API configuration | Fast response with GPT-4o and Claude 3.5/3.7 |

</div>

### 🚀 Quick Start

Follow the same setup instructions as above, but use `streamlit_app_en.py` for the English version.

#### 🔑 API Key Setup Guide

<div align="center">

| API | How to Get | Link |
|-----|------------|------|
| **OpenAI API** | Generate API key in OpenAI account | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **Anthropic API** | Generate API key in Anthropic account | [Anthropic Console](https://console.anthropic.com/) |
| **Tavily API** | Create free account on Tavily | [Tavily API](https://tavily.com/) |
| **Google Custom Search** | Enable Custom Search API in Google Cloud Console | [Google Custom Search](https://developers.google.com/custom-search/v1/overview) |
| **Google Maps API** | Enable Maps API in Google Cloud Console | [Google Maps Platform](https://developers.google.com/maps/documentation/javascript/get-api-key) |
| **Hotpepper API** | Create account on Recruit Web Service | [Hotpepper API](https://webservice.recruit.co.jp/doc/hotpepper/) |
| **Spotify API** | Create app in Spotify Developer | [Spotify Developer](https://developer.spotify.com/documentation/web-api) |

</div>

### 🎯 Available Agents

<div align="center">

| Agent | Function | Example |
|-------|----------|---------|
| 🧠 **Auto Selection** | Automatic agent selection | Any request |
| 🎼 **Music Expert** | Spotify track search & playlist retrieval | "Search Beatles songs" |
| 🎬 **Video Expert** | YouTube video search & information | "Programming tutorial videos" |
| 🗺️ **Travel Expert** | Hotel & Airbnb search | "Search hotels in Tokyo" |
| 🍽️ **Restaurant Expert** | Restaurant search & booking | "Italian restaurants in Shibuya" |
| 📅 **Scheduler** | Google Calendar management | "Schedule meeting tomorrow at 3 PM" |
| 🔢 **Math Expert** | Calculations & formula processing | "Complex mathematical calculations" |
| 🔬 **Research Expert** | Web search & information gathering | "Research latest AI technologies" |

</div>

### 💻 Usage

The English version provides the same functionality with an English interface. All features, analytics, and customization options are available in both languages.

---

<div align="center">

**⭐️ Star this project!**

If this project was helpful, please give it a star on GitHub.

</div> 