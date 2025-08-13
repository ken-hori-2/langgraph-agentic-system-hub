import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime
import io
import base64
from PIL import Image
import requests
from urllib.parse import quote
import re
import sys
import os

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# マルチエージェントシステムのインポート
try:
    from supervisor_workers_multiagents import app, run_agent, run_agent_music
except ImportError as e:
    st.error(f"インポートエラー: {e}")
    st.info("supervisor_workers_multiagents.pyファイルが見つかりません。")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="Agentic AI Multi-Agent Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS - app.pyを参考にしたモダンなデザイン
st.markdown("""
<style>
    /* メインコンテナのスタイル */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    /* チャットメッセージのスタイル */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .user-message {
        background: linear-gradient(135deg, #2c5282 0%, #1e3a8a 100%);
        border-left: 5px solid #3b82f6;
        color: #ffffff;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #553c9a 0%, #6b46c1 100%);
        border-left: 5px solid #a855f7;
        color: #ffffff;
    }
    
    .assistant-message-latest {
        background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%);
        border-left: 5px solid #a855f7;
        border: 3px solid #a855f7;
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4);
        animation: pulse 2s infinite;
        transform: scale(1.02);
        color: #ffffff;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 8px 25px rgba(156, 39, 176, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(156, 39, 176, 0.5); }
        100% { box-shadow: 0 8px 25px rgba(156, 39, 176, 0.3); }
    }
    
    /* カードのスタイル */
    .result-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #48bb78;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }
    
    .restaurant-card, .hotel-card, .video-card, .agent-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .restaurant-card:hover, .hotel-card:hover, .video-card:hover, .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }
    
    .error-card {
        background: linear-gradient(135deg, #742a2a 0%, #9b2c2c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #f56565;
        box-shadow: 0 4px 12px rgba(245, 101, 101, 0.3);
        color: #ffffff;
    }
    
    /* ボタンのスタイル */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* テキスト入力エリアのスタイル */
    .stTextArea textarea {
        border: 2px solid #667eea !important;
        border-radius: 15px !important;
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%) !important;
        color: #ffffff !important;
        font-size: 14px !important;
        padding: 15px !important;
        transition: all 0.3s ease !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.25) !important;
        background: linear-gradient(135deg, #1a1a2e 0%, #2d3748 100%) !important;
        outline: none !important;
        transform: scale(1.01) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #a0aec0 !important;
        font-style: italic !important;
    }
    
    /* テキストエリアのラベルスタイル */
    .stTextArea label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        margin-bottom: 10px !important;
    }
    
    /* 全体的な背景 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* テキストの可読性 */
    p, h1, h2, h3, h4, h5, h6, span, div {
        color: #ffffff !important;
    }
    
    /* サイドバーのスタイル */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        border-right: 2px solid #2d3748 !important;
    }
    
    /* タブのスタイル */
    [data-testid="stTabs"] {
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* メトリックカードのスタイル */
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 2px solid #4a5568;
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* Spotify埋め込みのスタイル */
    .spotify-embed {
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* プログレスバーのスタイル */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* セレクトボックスのスタイル */
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%) !important;
        border: 2px solid #667eea !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* チェックボックスのスタイル */
    .stCheckbox > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* リンクのスタイル */
    a {
        color: #90cdf4 !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #63b3ed !important;
        text-decoration: underline !important;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

def main():
    # ヘッダー
    st.markdown("""
    <div class="main-container">
        <h1>🧠 Agentic AI Multi-Agent Assistant</h1>
        <p>Specialized agents handle your diverse requests with intelligent orchestration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.markdown("### ✍️ Made by [ken-hori-2](https://github.com/ken-hori-2) 🚀")
        st.markdown("### 💻 [Project Repository](https://github.com/ken-hori-2/langgraph-agentic-system-hub/)") # src/langgraph-supervisor)")
        st.divider()
        
        st.markdown("### 🎯 エージェント選択")
        
        # エージェント選択
        agent_options = {
            "auto": "🧠 自動選択（推奨）",
            "music": "🎼 音楽エキスパート",
            "video": "🎬 動画エキスパート", 
            "travel": "🗺️ 旅行エキスパート",
            "restaurant": "🍽️ レストランエキスパート",
            "scheduler": "📅 スケジューラー",
            "math": "🔢 数学エキスパート",
            "research": "🔬 リサーチエキスパート"
        }
        
        selected_agent = st.selectbox(
            "使用するエージェントを選択してください",
            options=list(agent_options.keys()),
            format_func=lambda x: agent_options[x],
            index=0
        )
        
        st.session_state.current_agent = selected_agent
        
        st.divider()
        
        # システム設定
        st.markdown("### ⚙️ システム設定")
        
        # デバッグモード
        debug_mode = st.checkbox("🐛 デバッグモード", value=False)
        st.session_state.debug_mode = debug_mode
        
        # 最終回答表示オプション
        show_latest_only = st.checkbox("🎯 最新回答のみ表示", value=False)
        st.session_state.show_latest_only = show_latest_only
        
        st.divider()
        
        # クイックアクション
        st.markdown("### ⚡ クイックアクション")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎼 音楽", key="quick_music", use_container_width=True):
                st.session_state.current_agent = "music"
                st.session_state.quick_action = "music"
                st.rerun()
                
        with col2:
            if st.button("🍽️ レストラン", key="quick_restaurant", use_container_width=True):
                st.session_state.current_agent = "restaurant"
                st.session_state.quick_action = "restaurant"
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🗺️ 旅行", key="quick_travel", use_container_width=True):
                st.session_state.current_agent = "travel"
                st.session_state.quick_action = "travel"
                st.rerun()
                
        with col4:
            if st.button("🎬 動画", key="quick_video", use_container_width=True):
                st.session_state.current_agent = "video"
                st.session_state.quick_action = "video"
                st.rerun()
        
        st.divider()
        
        # 統計情報
        st.markdown("### 📊 統計情報")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("会話数", len(st.session_state.chat_history))
        with col2:
            st.metric("処理時間", f"{st.session_state.get('avg_processing_time', 0):.1f}秒")
        
        st.divider()
        
        # アクションボタン
        st.markdown("### 🔄 アクション")
        
        # クリアボタン
        if st.button("🗑️ チャット履歴をクリア", use_container_width=True, type="primary"):
            st.session_state.chat_history = []
            st.success("✅ チャット履歴をクリアしました。")
            st.rerun()
    
    # メインコンテンツ
    tab1, tab2, tab3 = st.tabs(["💬 チャット", "📊 分析", "⚙️ 設定"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        analytics_interface()
    
    with tab3:
        settings_interface()

def chat_interface():
    # クイックアクションの処理
    if hasattr(st.session_state, 'quick_action'):
        quick_action = st.session_state.quick_action
        del st.session_state.quick_action
        
        if quick_action == "music":
            st.info("🎼 音楽エキスパートモードです。アーティスト名や曲名を入力してください。")
        elif quick_action == "restaurant":
            st.info("🍽️ レストランエキスパートモードです。エリアや料理ジャンルを入力してください。")
        elif quick_action == "travel":
            st.info("🗺️ 旅行エキスパートモードです。宿泊地や日付を入力してください。")
        elif quick_action == "video":
            st.info("🎬 動画エキスパートモードです。動画の検索キーワードを入力してください。")
    
    # チャット履歴の表示
    chat_container = st.container()
    
    with chat_container:
        # デバッグ情報を表示
        if st.session_state.get('debug_mode', False):
            with st.expander("🐛 デバッグ情報", expanded=False):
                st.write("**チャット履歴デバッグ:**")
                st.write(f"履歴数: {len(st.session_state.chat_history)}")
                for i, msg in enumerate(st.session_state.chat_history):
                    st.write(f"メッセージ {i}: role={msg.get('role')}, content_length={len(msg.get('content', ''))}")
        
        # 最新回答のみ表示オプションが有効な場合
        if st.session_state.get('show_latest_only', False) and st.session_state.chat_history:
            # 最新のAI回答のみを表示
            latest_ai_message = None
            for msg in reversed(st.session_state.chat_history):
                if msg["role"] == "assistant":
                    latest_ai_message = msg
                    break
            
            if latest_ai_message:
                st.markdown("### 🎯 最新の回答")
                
                if "results" in latest_ai_message and latest_ai_message["results"]:
                    tab1, tab2 = st.tabs(["🤖 AI回答", "📊 詳細結果"])
                    
                    with tab1:
                        st.markdown(f"""
                        <div class="chat-message assistant-message-latest">
                            <strong>🤖 AI:</strong><br>
                            {latest_ai_message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with tab2:
                        display_results(latest_ai_message["results"])
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message-latest">
                        <strong>🤖 AI:</strong><br>
                        {latest_ai_message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # 全履歴を表示
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 あなた:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 最終回答かどうかを判定
                    is_last_response = (i == len(st.session_state.chat_history) - 1)
                    
                    # デバッグ情報を表示
                    if st.session_state.get('debug_mode', False) and is_last_response:
                        with st.expander("🐛 最新回答デバッグ", expanded=False):
                            st.write(f"**最新回答デバッグ:** content_length={len(message.get('content', ''))}")
                    
                    # AI回答をタブで表示
                    if "results" in message and message["results"]:
                        # 結果がある場合はタブで表示
                        if is_last_response:
                            st.markdown("### 🎯 最新の回答")
                        
                        tab1, tab2 = st.tabs(["🤖 AI回答", "📊 詳細結果"])
                        
                        with tab1:
                            message_style = "assistant-message" if not is_last_response else "assistant-message-latest"
                            st.markdown(f"""
                            <div class="chat-message {message_style}">
                                <strong>🤖 AI:</strong><br>
                                {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with tab2:
                            display_results(message["results"])
                    else:
                        # 結果がない場合は通常表示
                        message_style = "assistant-message" if not is_last_response else "assistant-message-latest"
                        if is_last_response:
                            st.markdown("### 🎯 最新の回答")
                        
                        st.markdown(f"""
                        <div class="chat-message {message_style}">
                            <strong>🤖 AI:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
    
    # 入力フォーム
    st.markdown("---")
    
    # 入力エリア
    user_input = st.text_area(
        "メッセージを入力してください",
        placeholder="例: 渋谷のイタリアンを探して、明日の15時に会議を予定に入れて、ビートルズの曲を教えて...",
        height=100,
        key=f"user_input_{len(st.session_state.chat_history)}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 送信", type="primary", disabled=st.session_state.processing, use_container_width=True):
            if user_input.strip():
                process_user_input(user_input)
                # チャット履歴を更新してテキストエリアをクリア
                st.rerun()
    
    with col2:
        if st.button("🔄 リセット", disabled=st.session_state.processing, use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ チャット履歴をリセットしました。")
            st.rerun()
    
    with col3:
        if st.session_state.processing:
            st.info("🔄 処理中...")
        
        # テスト用ボタン
        if st.button("🧪 テスト回答", disabled=st.session_state.processing, use_container_width=True):
            test_response = "これはテスト回答です。AIの回答が正常に表示されるかテストしています。"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": test_response,
                "results": [],
                "timestamp": datetime.now()
            })
            st.success("✅ テスト回答を追加しました。")
            st.rerun()

def process_user_input(user_input):
    st.session_state.processing = True
    
    # ユーザーメッセージを履歴に追加
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # プログレスバー
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🤖 AIエージェントが処理中...")
        progress_bar.progress(25)
        
        start_time = time.time()
        
        # エージェントの実行
        try:
            if st.session_state.current_agent == "auto":
                result = run_agent([{"role": "user", "content": user_input}])
            else:
                # 特定のエージェントを指定した場合
                result = run_agent([{"role": "user", "content": user_input}])
        except Exception as agent_error:
            st.warning(f"エージェント実行エラー: {str(agent_error)}")
            # フォールバック: シンプルな応答を生成
            result = {
                "text": f"申し訳ございません。現在エージェントシステムに問題があります。\n\nリクエスト: {user_input}\n\nエラー: {str(agent_error)}\n\nしばらく時間をおいてから再度お試しください。",
                "results": []
            }
        
        processing_time = time.time() - start_time
        
        progress_bar.progress(100)
        status_text.text("✅ 完了!")
        
        # Add result to history
        response_text = result.get("text", "回答を生成できませんでした。")
        response_results = result.get("results", [])
        
        # Debug information display (development only)
        if st.session_state.get('debug_mode', False):
            st.write("**デバッグ情報:**")
            st.write(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            st.write(f"Response text: {response_text}")
            st.write(f"Response results: {response_results}")
            st.write(f"Response text type: {type(response_text)}")
            st.write(f"Response text length: {len(response_text) if response_text else 0}")
            
            # Display raw result
            st.write("**生の結果:**")
            st.json(result)
        
        # Check if result is not empty
        if not response_text or response_text.strip() == "":
            st.error("⚠️ AIの回答が空です。デバッグモードを有効にして詳細を確認してください。")
            response_text = "AIの回答を取得できませんでした。デバッグモードを有効にして詳細を確認してください。"
        
        # resultsがNoneの場合は空リストに変換
        if response_results is None:
            response_results = []
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text,
            "results": response_results,
            "timestamp": datetime.now(),
            "processing_time": processing_time
        })
        
        # 平均処理時間を更新
        if 'avg_processing_time' not in st.session_state:
            st.session_state.avg_processing_time = processing_time
        else:
            st.session_state.avg_processing_time = (
                st.session_state.avg_processing_time + processing_time
            ) / 2
        
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"申し訳ございません。エラーが発生しました: {str(e)}\n\nシステムを再起動するか、しばらく時間をおいてから再度お試しください。",
            "timestamp": datetime.now()
        })
    finally:
        st.session_state.processing = False
        progress_bar.empty()
        status_text.empty()

def display_results(results):
    """Display results appropriately"""
    if not results:
        st.info("📊 詳細結果はありません。")
        return
    
    # Determine result type
    if isinstance(results, list):
        if results and isinstance(results[0], dict):
            # Restaurant results
            if 'name' in results[0] and 'cuisine' in results[0]:
                display_restaurant_results(results)
            # Hotel results
            elif 'name' in results[0] and 'price' in results[0] and 'amenities' in results[0]:
                display_hotel_results(results)
            # Video results
            elif 'title' in results[0] and 'channel' in results[0]:
                display_video_results(results)
            # Spotify results
            elif 'name' in results[0] and 'artist' in results[0] and 'spotify_url' in results[0]:
                display_spotify_results(results)
            else:
                st.json(results)
        else:
            st.write(results)
    elif isinstance(results, dict):
        st.json(results)
    else:
        st.write(results)

def display_restaurant_results(restaurants):
    """レストラン結果を表示"""
    st.markdown("### 🍽️ レストラン検索結果")
    
    for i, restaurant in enumerate(restaurants):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="restaurant-card">
                    <h4>🍽️ {restaurant.get('name', 'N/A')}</h4>
                    <p><strong>ジャンル:</strong> {restaurant.get('cuisine', 'N/A')}</p>
                    <p><strong>予算:</strong> {restaurant.get('budget', 'N/A')}</p>
                    <p><strong>評価:</strong> {restaurant.get('rating', 'N/A')}</p>
                    <p><strong>住所:</strong> {restaurant.get('address', 'N/A')}</p>
                    <p><strong>営業時間:</strong> {restaurant.get('hours', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if restaurant.get('google_maps_url'):
                    st.markdown(f"""
                    <a href="{restaurant['google_maps_url']}" target="_blank">
                        <button style="background: #4285f4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            🗺️ Googleマップ
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                
                if restaurant.get('directions_url'):
                    st.markdown(f"""
                    <a href="{restaurant['directions_url']}" target="_blank">
                        <button style="background: #34a853; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            🚇 経路案内
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_hotel_results(hotels):
    """ホテル結果を表示"""
    st.markdown("### 🏨 ホテル検索結果")
    
    for i, hotel in enumerate(hotels):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="hotel-card">
                    <h4>🏨 {hotel.get('name', 'N/A')}</h4>
                    <p><strong>価格:</strong> {hotel.get('price', 'N/A')}</p>
                    <p><strong>評価:</strong> {hotel.get('rating', 'N/A')}</p>
                    <p><strong>アメニティ:</strong> {', '.join(hotel.get('amenities', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if hotel.get('url'):
                    st.markdown(f"""
                    <a href="{hotel['url']}" target="_blank">
                        <button style="background: #ff6b6b; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            📖 詳細を見る
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_video_results(videos):
    """動画結果を表示"""
    st.markdown("### 📹 動画検索結果")
    
    for i, video in enumerate(videos):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if video.get('thumbnail'):
                    st.image(video['thumbnail'], width=200)
            
            with col2:
                st.markdown(f"""
                <div class="video-card">
                    <h4>📹 {video.get('title', 'N/A')}</h4>
                    <p><strong>チャンネル:</strong> {video.get('channel', 'N/A')}</p>
                    <p><strong>説明:</strong> {video.get('description', 'N/A')[:100]}...</p>
                    <p><strong>公開日:</strong> {video.get('published_at', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if video.get('youtube_url'):
                    st.markdown(f"""
                    <a href="{video['youtube_url']}" target="_blank">
                        <button style="background: #ff0000; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            ▶️ YouTubeで見る
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_spotify_results(tracks):
    """Spotify結果を表示"""
    st.markdown("### 🎵 音楽検索結果")
    
    for i, track in enumerate(tracks):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if track.get('album_art'):
                    st.image(track['album_art'], width=150)
            
            with col2:
                st.markdown(f"""
                <div class="agent-card">
                    <h4>🎵 {track.get('name', 'N/A')}</h4>
                    <p><strong>アーティスト:</strong> {track.get('artist', 'N/A')}</p>
                    <p><strong>アルバム:</strong> {track.get('album', 'N/A')}</p>
                    <p><strong>リリース日:</strong> {track.get('release_date', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if track.get('spotify_url'):
                    # Spotify埋め込みプレイヤー
                    track_id = track['spotify_url'].split('track/')[-1].split('?')[0]
                    embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                    st.markdown(f"""
                    <div class="spotify-embed">
                        <iframe src="{embed_url}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    </div>
                    """, unsafe_allow_html=True)

def analytics_interface():
    """分析インターフェース"""
    st.markdown("## 📊 分析ダッシュボード")
    
    if not st.session_state.chat_history:
        st.info("チャット履歴がありません。まずはチャットを開始してください。")
        return
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 総メッセージ数</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.chat_history)), unsafe_allow_html=True)
    
    with col2:
        user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
        st.markdown("""
        <div class="metric-card">
            <h3>👤 ユーザーメッセージ数</h3>
            <h2>{}</h2>
        </div>
        """.format(len(user_messages)), unsafe_allow_html=True)
    
    with col3:
        assistant_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "assistant"]
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI回答数</h3>
            <h2>{}</h2>
        </div>
        """.format(len(assistant_messages)), unsafe_allow_html=True)
    
    with col4:
        avg_time = st.session_state.get('avg_processing_time', 0)
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ 平均処理時間</h3>
            <h2>{:.1f}秒</h2>
        </div>
        """.format(avg_time), unsafe_allow_html=True)
    
    st.divider()
    
    # 時系列グラフ
    st.markdown("### 📈 メッセージ時系列")
    
    if len(st.session_state.chat_history) > 1:
        df = pd.DataFrame([
            {
                'timestamp': msg['timestamp'],
                'role': msg['role'],
                'content_length': len(msg['content'])
            }
            for msg in st.session_state.chat_history
        ])
        
        fig = px.line(df, x='timestamp', y='content_length', color='role',
                     title='メッセージ長の時系列変化',
                     color_discrete_map={'user': '#2196f3', 'assistant': '#9c27b0'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 処理時間の分布
    processing_times = [
        msg.get('processing_time', 0) 
        for msg in st.session_state.chat_history 
        if msg["role"] == "assistant" and msg.get('processing_time')
    ]
    
    if processing_times:
        st.markdown("### ⏱️ 処理時間分布")
        fig = px.histogram(x=processing_times, title='処理時間の分布',
                          labels={'x': '処理時間（秒）', 'y': '頻度'},
                          color_discrete_sequence=['#667eea'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333')
        )
        st.plotly_chart(fig, use_container_width=True)

def settings_interface():
    """設定インターフェース"""
    st.markdown("## ⚙️ 設定")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔧 アプリケーション設定")
        
        # テーマ設定
        theme = st.selectbox(
            "テーマ",
            ["light", "dark"],
            index=0
        )
        
        # 言語設定
        language = st.selectbox(
            "言語",
            ["日本語", "English"],
            index=0
        )
        
        # 自動保存設定
        auto_save = st.checkbox("チャット履歴を自動保存", value=True)
        
        # 通知設定
        notifications = st.checkbox("処理完了時に通知", value=True)
        
        # 設定を保存
        if st.button("💾 設定を保存", type="primary", use_container_width=True):
            st.success("✅ 設定を保存しました。")
    
    with col2:
        st.markdown("### 📊 エージェント情報")
        
        agents_info = {
            "music": "🎼 音楽エキスパート - Spotify検索、プレイリスト取得",
            "video": "🎬 動画エキスパート - YouTube検索、動画情報取得",
            "travel": "🗺️ 旅行エキスパート - ホテル・Airbnb検索",
            "restaurant": "🍽️ レストランエキスパート - レストラン検索・予約",
            "scheduler": "📅 スケジューラー - Googleカレンダー管理",
            "math": "🔢 数学エキスパート - 計算・数式処理",
            "research": "🔬 リサーチエキスパート - Web検索・情報収集"
        }
        
        for agent, description in agents_info.items():
            st.info(description)
    
    st.divider()
    
    st.markdown("### 🔑 API設定")
    st.info("API設定は.envファイルで管理されています。")
    
    # API設定の確認
    with st.expander("🔍 API設定確認", expanded=False):
        api_keys = {
            "OpenAI API Key": os.environ.get("OPENAI_API_KEY", "未設定"),
            "Anthropic API Key": os.environ.get("ANTHROPIC_API_KEY", "未設定"),
            "Google Maps API Key": os.environ.get("GOOGLE_MAPS_API_KEY", "未設定"),
            "Spotify Client ID": os.environ.get("SPOTIFY_USER_ID", "未設定"),
            "Recruit API Key": os.environ.get("RECRUIT_API_KEY", "未設定")
        }
        
        for key_name, key_value in api_keys.items():
            if key_value != "未設定":
                st.success(f"✅ {key_name}: 設定済み")
            else:
                st.warning(f"⚠️ {key_name}: 未設定")

if __name__ == "__main__":
    main() 