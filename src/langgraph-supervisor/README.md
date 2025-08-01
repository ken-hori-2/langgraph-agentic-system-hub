# LangGraph Supervisor システム

このフォルダは、LangGraphを使用したマルチエージェントシステムのスーパーバイザー実装です。複数の専門エージェントを統合し、ユーザーのリクエストに応じて適切なエージェントを選択・実行するシステムです。

## 📁 ファイル構成

### メインファイル

- **`main_latest.py`** (2,336行) - 最新のメインシステム
  - 7つの専門エージェントを統合したスーパーバイザーシステム
  - 最も完全な機能を持つバージョン

- **`main.py`** (1,251行) - 基本システム
  - 基本的なエージェント機能を提供
  - 開発・テスト用の軽量版

- **`main copy.py`** (2,630行) - バックアップ版
  - 開発過程でのバックアップファイル

### Streamlitアプリケーション

- **`restaurant_streamlit_app.py`** (118行) - レストラン検索アプリ
  - HotPepper + Google Maps統合検索
  - 予算・ジャンル・エリアでの絞り込み
  - 総合評価順での表示

- **`music_streamlit_app.py`** (50行) - 音楽検索アプリ
  - Spotify楽曲検索
  - 埋め込みプレイヤー付き表示
  - モダンUI

### その他

- **`workflow.png`** - システムのワークフロー図
- **`__pycache__/`** - Pythonキャッシュファイル

## 🏗️ システム構成

### スーパーバイザーシステム

`main_latest.py`では以下の7つの専門エージェントを統合しています：

1. **research_expert** - 研究・情報収集
   - Web検索、現在時刻取得

2. **math_expert** - 数学計算
   - 加算、乗算

3. **scheduler_expert** - スケジュール管理
   - Google Calendar連携
   - 相対日付計算

4. **music_expert** - 音楽
   - Spotify楽曲・アーティスト・プレイリスト検索

5. **video_expert** - 動画
   - YouTube動画検索・情報取得

6. **travel_expert** - 旅行
   - Jalan.netホテル検索
   - Airbnb宿泊施設検索

7. **restaurant_expert** - レストラン
   - HotPepper Gourmet API
   - Google Maps Places API
   - 予約状況確認

## 🚀 使い方

### 1. メインシステムの実行

```bash
# 最新版を実行
python main_latest.py

# 基本版を実行
python main.py
```

実行すると対話型のインターフェースが起動し、ユーザーの質問に応じて適切なエージェントが自動選択されます。

### 2. Streamlitアプリの実行

```bash
# レストラン検索アプリ
streamlit run restaurant_streamlit_app.py

# 音楽検索アプリ
streamlit run music_streamlit_app.py
```

## 🔧 主要機能

### スケジュール管理
- Google Calendar連携
- 相対日付対応（「明日」「来週月曜日」など）
- 自動的な日時計算

### レストラン検索
- HotPepper Gourmet API統合
- Google Maps Places API統合
- エリア・ジャンル・予算での絞り込み
- 予約状況確認
- 経路案内URL生成

### 音楽検索
- Spotify API統合
- 楽曲・アーティスト・プレイリスト検索
- 埋め込みプレイヤー表示

### 旅行・宿泊
- Jalan.netスクレイピング
- Airbnb.comスクレイピング
- リアルタイム価格・空室情報

### 動画検索
- YouTube API統合
- 動画情報取得
- 検索結果の詳細表示

## 📋 必要な環境変数

`.env`ファイルに以下の設定が必要です：

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Google Calendar API
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# HotPepper Gourmet API
HOTPEPPER_API_KEY=your_hotpepper_api_key

# Tavily Search API
TAVILY_API_KEY=your_tavily_api_key
```

## 🛠️ 依存関係

主要な依存パッケージ：

```python
langchain_openai
langgraph_supervisor
langgraph
langchain_tavily
google-auth
google-api-python-client
requests
streamlit
pydantic
python-dotenv
```

## 📊 データモデル

### WorkflowState
```python
class WorkflowState(BaseModel):
    user_request: str
    extracted_schedule: Optional[ScheduleRequest]
    current_time: Optional[str]
    final_result: Optional[str]
```

### ScheduleRequest
```python
class ScheduleRequest(BaseModel):
    event: str
    time: datetime.datetime
```

## 🔄 ワークフロー

1. ユーザーが質問を入力
2. スーパーバイザーが現在時刻を取得
3. 質問内容を分析して適切なエージェントを選択
4. 選択されたエージェントが専門ツールを使用して処理
5. 結果を統合してユーザーに返答

## 🎯 使用例

### レストラン検索
```
ユーザー: "渋谷のイタリアンを3000円以下で探して"
→ restaurant_expertが選択され、HotPepper APIで検索
```

### 音楽検索
```
ユーザー: "ビートルズの曲を教えて"
→ music_expertが選択され、Spotify APIで検索
```

### スケジュール管理
```
ユーザー: "明日の15時に会議を予定に入れて"
→ scheduler_expertが選択され、Google Calendarに追加
```

## 📈 開発履歴

- `main.py` - 基本実装
- `main copy.py` - 機能拡張版
- `main_latest.py` - 最新の完全版（推奨）

## 🐛 トラブルシューティング

### よくある問題

1. **APIキーエラー**
   - 環境変数が正しく設定されているか確認
   - APIキーの有効期限を確認

2. **依存関係エラー**
   ```bash
   pip install -r requirements.txt
   ```

3. **Google Calendar認証エラー**
   - サービスアカウントキーファイルのパスを確認
   - カレンダーIDの設定を確認

## 📝 注意事項

- 各APIの利用制限に注意
- スクレイピング機能は利用規約を遵守
- 個人情報の取り扱いに注意

## 🤝 貢献

バグ報告や機能要望は、適切な形式で報告してください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。 