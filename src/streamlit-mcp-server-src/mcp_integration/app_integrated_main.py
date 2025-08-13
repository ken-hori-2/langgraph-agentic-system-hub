import streamlit as st
import asyncio
import nest_asyncio
import json
import os
import platform
import requests
from urllib.parse import quote
import re
from collections import defaultdict

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Apply nest_asyncio: Allow nested calls within an already running event loop
nest_asyncio.apply()

# Create and reuse global event loop (create once and continue using)
if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from utils import astream_graph, random_uuid
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

# Load environment variables
load_dotenv(override=True)

# config.json file path setting
CONFIG_FILE_PATH = "config.json"

# --- Tool Definitions (for Agent) ---
@tool
def search_spotify_tracks_tool(query: str, limit: int = 10) -> str:
    """Spotifyで楽曲を検索するツール（Agent用）
    
    Args:
        query: 検索クエリ（アーティスト名、曲名、ジャンルなど）
        limit: 取得する楽曲数（デフォルト: 10）
    
    Returns:
        検索結果のJSON文字列
    """
    return search_spotify_tracks_func(query, limit)

@tool
def search_restaurants_tool(location: str, cuisine: str = "", budget: str = "", count: int = 20) -> str:
    """レストランを検索するツール（Agent用）
    
    Args:
        location: 検索する場所（必須）
        cuisine: 料理ジャンル（オプション）
        budget: 予算（オプション）
        count: 取得する件数（デフォルト: 20）
    
    Returns:
        検索結果のJSON文字列
    """
    return search_restaurants_func(location, cuisine, budget, count)

# --- Function Definitions (for UI) ---
def search_spotify_tracks_func(query: str, limit: int = 10) -> dict:
    """Spotifyで楽曲を検索する関数（UI用）"""
    try:
        client_id = os.getenv("SPOTIFY_USER_ID")
        client_secret = os.getenv("SPOTIFY_TOKEN")
        
        if not client_id or not client_secret:
            return {"error": "Spotify API credentials not configured. Please set SPOTIFY_USER_ID and SPOTIFY_TOKEN in your .env file."}
        
        # Get access token
        auth_response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        
        if auth_response.status_code != 200:
            return {"error": "Failed to authenticate with Spotify API"}
        
        access_token = auth_response.json()['access_token']
        
        # Search for tracks
        headers = {'Authorization': f'Bearer {access_token}'}
        search_response = requests.get(
            f'https://api.spotify.com/v1/search?q={quote(query)}&type=track&limit={limit}',
            headers=headers
        )
        
        if search_response.status_code != 200:
            return {"error": "Failed to search Spotify API"}
        
        tracks_data = search_response.json()['tracks']['items']
        results = []
        
        for track in tracks_data:
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'],
                'spotify_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity']
            }
            results.append(track_info)
        
        return {
            "message": f"{len(results)}件の楽曲が見つかりました",
            "tracks": results
        }
        
    except Exception as e:
        return {"error": f"Spotify search error: {str(e)}"}

def search_restaurants_func(location: str, cuisine: str = "", budget: str = "", count: int = 20) -> dict:
    """レストランを検索する関数（UI用）"""
    try:
        # HotPepperで検索
        hp_result = search_hotpepper_restaurants(location, cuisine, budget)
        hp_restaurants = hp_result.get("restaurants", []) if "error" not in hp_result else []
        
        # Google Mapsで検索
        gm_result = search_google_maps_restaurants(location, cuisine)
        gm_restaurants = gm_result.get("restaurants", []) if "error" not in gm_result else []
        
        # 結果を統合
        merged_restaurants = merge_restaurant_info(hp_restaurants, gm_restaurants)
        
        # 指定された件数に制限
        merged_restaurants = merged_restaurants[:count]
        
        return {
            "message": f"{len(merged_restaurants)}件のレストランが見つかりました",
            "restaurants": merged_restaurants,
            "hotpepper_count": len(hp_restaurants),
            "google_maps_count": len(gm_restaurants)
        }
        
    except Exception as e:
        return {"error": f"Restaurant search error: {str(e)}"}

# --- Helper Functions ---
def search_hotpepper_restaurants(location: str, cuisine: str = "", budget: str = "") -> dict:
    """HotPepperでレストランを検索する"""
    try:
        api_key = os.getenv("HOTPEPPER_API_KEY")
        if not api_key:
            return {"error": "HotPepper API key not configured"}
        
        # Build search parameters
        params = {
            'key': api_key,
            'format': 'json',
            'count': 20
        }
        
        if location:
            params['address'] = location
        if cuisine:
            params['genre'] = cuisine
        if budget:
            params['budget'] = budget
        
        response = requests.get('https://webservice.recruit.co.jp/hotpepper/gourmet/v1/', params=params)
        
        if response.status_code != 200:
            return {"error": "Failed to search HotPepper"}
        
        data = response.json()
        shops = data.get('results', {}).get('shop', [])
        
        restaurants = []
        for shop in shops:
            restaurant_info = {
                'name': shop['name'],
                'address': shop['address'],
                'cuisine': shop['genre']['name'],
                'budget': shop['budget']['name'],
                'rating': shop.get('rating', '評価なし'),
                'url': shop['urls']['pc']
            }
            restaurants.append(restaurant_info)
        
        return {
            "message": f"{len(restaurants)}件のレストランが見つかりました",
            "restaurants": restaurants
        }
        
    except Exception as e:
        return {"error": f"HotPepper search error: {str(e)}"}

def search_google_maps_restaurants(location: str, cuisine: str = "", radius: int = 1000) -> dict:
    """Google Mapsでレストランを検索する"""
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return {"error": "Google Maps API key not configured"}
        
        # Build search query
        query = f"restaurants in {location}"
        if cuisine:
            query += f" {cuisine}"
        
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': api_key,
            'radius': radius,
            'type': 'restaurant'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": "Failed to search Google Maps"}
        
        data = response.json()
        places = data.get('results', [])
        
        restaurants = []
        for place in places:
            restaurant_info = {
                'name': place['name'],
                'address': place.get('formatted_address', '住所不明'),
                'rating': place.get('rating', '評価なし'),
                'price_level': place.get('price_level', '価格不明'),
                'google_maps_url': f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}"
            }
            restaurants.append(restaurant_info)
        
        return {
            "message": f"{len(restaurants)}件のレストランが見つかりました",
            "restaurants": restaurants
        }
        
    except Exception as e:
        return {"error": f"Google Maps search error: {str(e)}"}

def merge_restaurant_info(hp_list, gm_list):
    """HotPepperとGoogle Mapsの結果を統合する"""
    merged = []
    for hp in hp_list:
        best_match = None
        for gm in gm_list:
            if (hp['name'] and gm['name'] and 
                (hp['name'] in gm['name'] or gm['name'] in hp['name'])):
                best_match = gm
                break
        
        merged_info = hp.copy()
        if best_match:
            if not merged_info.get('rating') or merged_info['rating'] == '評価なし':
                merged_info['rating'] = best_match.get('rating', merged_info.get('rating'))
            merged_info['google_rating'] = best_match.get('rating')
            merged_info['google_maps_url'] = best_match.get('google_maps_url')
        merged.append(merged_info)
    
    # Add Google-only restaurants
    hp_names = set([r['name'] for r in hp_list])
    for gm in gm_list:
        if gm['name'] not in hp_names:
            merged.append(gm)
    
    return merged

def show_spotify_embeds_streamlit(tracks, title="Spotify埋め込みプレイヤー"):
    """Spotify埋め込みプレイヤーを表示"""
    st.markdown(f"### {title}")
    for track in tracks:
        url = track.get('spotify_url')
        if url and 'track/' in url:
            track_id = url.split('track/')[-1].split('?')[0]
            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
            st.markdown(
                f'''
                <div class="spotify-embed-container" style="
                    border-radius: 12px; 
                    overflow: hidden; 
                    width: 100%; 
                    height: 152px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border: 1px solid #e0e0e0;
                    background: #191414;
                ">
                    <iframe 
                        src="{embed_url}" 
                        width="100%" 
                        height="152" 
                        frameborder="0" 
                        allowtransparency="true" 
                        allow="encrypted-media"
                        loading="lazy"
                    ></iframe>
                </div>
                ''',
                unsafe_allow_html=True
            )

def show_googlemap_embed_streamlit(address_or_query, title="Googleマップ埋め込み"):
    """Googleマップ埋め込みを表示"""
    query = quote(address_or_query)
    embed_url = f"https://www.google.com/maps?q={query}&output=embed"
    
    # モダンなスタイルでマップを表示
    st.markdown(
        f'''
        <div style="
            border-radius: 12px; 
            overflow: hidden; 
            width: 100%; 
            height: 200px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            margin: 8px 0;
        ">
            <iframe 
                src="{embed_url}" 
                width="100%" 
                height="200" 
                frameborder="0" 
                style="border-radius: 12px;" 
                allowfullscreen
                loading="lazy"
            ></iframe>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Function to load settings from JSON file
def load_config_from_json():
    """
    Loads settings from config.json file.
    Creates a file with default settings if it doesn't exist.
    """
    default_config = {
        "get_current_time": {
            "command": "python",
            "args": ["./mcp_server_time.py"],
            "transport": "stdio"
        }
    }
    
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            save_config_to_json(default_config)
            return default_config
    except Exception as e:
        st.error(f"Error loading settings file: {str(e)}")
        return default_config

# Function to save settings to JSON file
def save_config_to_json(config):
    """Saves settings to config.json file."""
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving settings file: {str(e)}")
        return False

# Initialize login session variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Check if login is required
use_login = os.environ.get("USE_LOGIN", "false").lower() == "true"

# Change page settings based on login status
if use_login and not st.session_state.authenticated:
    st.set_page_config(page_title="Integrated Agent System", page_icon="🧠")
else:
    st.set_page_config(page_title="Integrated Agent System", page_icon="🧠", layout="wide")

# カスタムCSSでSpotify埋め込みの余白を調整
st.markdown("""
<style>
    /* Spotify埋め込みプレイヤーの余白を完全に削除 */
    .spotify-embed-container {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 0 !important;
        font-size: 0 !important;
        height: 152px !important;
        overflow: hidden !important;
        display: block !important;
        position: relative !important;
        border: none !important;
        min-height: 152px !important;
        max-height: 152px !important;
        box-sizing: border-box !important;
    }
    
    .spotify-embed-container iframe {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        display: block !important;
        line-height: 0 !important;
        vertical-align: top !important;
        height: 152px !important;
        width: 100% !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        min-height: 152px !important;
        max-height: 152px !important;
        box-sizing: border-box !important;
    }
    
    /* Spotifyの埋め込み要素の余白を削除 */
    .spotify-embed-container iframe[src*="spotify.com"] {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        display: block !important;
        line-height: 0 !important;
        vertical-align: top !important;
        height: 152px !important;
        width: 100% !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        min-height: 152px !important;
        max-height: 152px !important;
        box-sizing: border-box !important;
    }
    
    /* Spotify埋め込みコンテナ内の要素の余白を削除 */
    .spotify-embed-container * {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 0 !important;
        font-size: 0 !important;
        box-sizing: border-box !important;
    }
</style>
""", unsafe_allow_html=True)

# Display login screen if login feature is enabled and not yet authenticated
if use_login and not st.session_state.authenticated:
    st.title("🔐 Login")
    st.markdown("Login is required to use the system.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            expected_username = os.environ.get("USER_ID")
            expected_password = os.environ.get("USER_PASSWORD")

            if username == expected_username and password == expected_password:
                st.session_state.authenticated = True
                st.success("✅ Login successful! Please wait...")
                st.rerun()
            else:
                st.error("❌ Username or password is incorrect.")

    st.stop()

# Add author information at the top of the sidebar
st.sidebar.markdown("### ✍️ Made by [ken-hori-2](https://github.com/ken-hori-2) 🚀")
st.sidebar.markdown(
    "### 💻 [Project Page](https://ken-hori-2.github.io/langgraph-agentic-system-hub/portfolio/)"
)

st.sidebar.divider()

# Main title and description
# st.title("🎵🍽️ Integrated Music & Restaurant Search System")
st.title("💬 MCP Tool Utilization Agent System (Integrated Music🎵 & Restaurant🍽️ Search with Preview)")
st.markdown("✨ Search for music on Spotify and restaurants with HotPepper + Google Maps integration.")

# Initialize session variables
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False
    st.session_state.agent = None
    st.session_state.mcp_client = None
    st.session_state.timeout_seconds = 120
    st.session_state.selected_model = "gpt-4o-mini"
    st.session_state.recursion_limit = 100

if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Initialize MCP tools expander state
if "mcp_tools_expander" not in st.session_state:
    st.session_state.mcp_tools_expander = False

# Initialize pending MCP config
if "pending_mcp_config" not in st.session_state:
    st.session_state.pending_mcp_config = load_config_from_json()

# Initialize MCP config text
if "mcp_config_text" not in st.session_state:
    st.session_state.mcp_config_text = json.dumps(
        st.session_state.pending_mcp_config, indent=2, ensure_ascii=False
    )

# --- MCP Functions ---
async def cleanup_mcp_client():
    """
    Safely terminates the existing MCP client.

    Properly releases resources if an existing client exists.
    """
    if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
        try:
            st.session_state.mcp_client = None
        except Exception as e:
            import traceback
            # st.warning(f"Error while terminating MCP client: {str(e)}")
            # st.warning(traceback.format_exc())

async def initialize_session(mcp_config=None):
    """
    Initializes MCP session and agent.
    MCPセッションとエージェントを初期化します。

    Args:
        mcp_config: MCP tool configuration information (JSON). Uses default settings if None
        mcp_config: MCPツールの設定情報（JSON）。Noneの場合はデフォルト設定を使用

    Returns:
        bool: Initialization success status
        bool: 初期化の成功状態
    """
    with st.spinner("🔄 Connecting to MCP server..."):
        # First safely clean up existing client
        # 既存のMCPクライアントを安全に終了
        await cleanup_mcp_client()

        # 設定の読み込み
        if mcp_config is None:
            # Load settings from config.json file
            # config.jsonファイルから設定を読み込む
            mcp_config = load_config_from_json()
        
        # MCPクライアントの初期化
        # Initialize MCP client
        # このクライアントはconfig.jsonで定義された各MCPサーバーに接続します
        client = MultiServerMCPClient(mcp_config)
        
        # 各MCPサーバーからツールを取得
        # Get tools from each MCP server
        # 例：get_current_time, tavily_search, spotify_searchなどのツール
        mcp_tools = await client.get_tools()
        st.session_state.mcp_client = client

        # カスタムツールを定義
        custom_tools = [
            search_spotify_tracks_tool,
            search_restaurants_tool
        ]
        
        # MCPツールとカスタムツールを組み合わせ
        all_tools = mcp_tools + custom_tools
        st.session_state.tool_count = len(all_tools)

        # Initialize appropriate model based on selection
        # 選択されたモデルに基づいて適切なLLMを初期化
        selected_model = st.session_state.selected_model

        # OpenAIモデルの場合
        # For OpenAI models
        model = ChatOpenAI(
            model=selected_model,
            temperature=0.1,
            max_tokens=16000,  # Default for OpenAI models
        )

        # React Agentの作成
        # Create React Agent
        # このエージェントは以下の要素で構成されます：
        # This agent consists of the following components:
        # 1. LLMモデル（上記で初期化したもの）
        # 1. LLM model (initialized above)
        # 2. ツール（MCPサーバーから取得したもの + カスタムツール）
        # 2. Tools (obtained from MCP servers + custom tools)
        # 3. チェックポイント（会話の状態を保存）
        # 3. Checkpoint (saves conversation state)
        agent = create_react_agent(
            model,        # 使用するLLMモデル / LLM model to use
            all_tools,    # MCPサーバーから取得したツール + カスタムツール / Tools obtained from MCP servers + custom tools
            checkpointer=MemorySaver(),  # 会話の状態を保存するチェックポイント / Checkpoint to save conversation state
        )
        
        # セッション状態の更新
        # Update session state
        st.session_state.agent = agent
        st.session_state.session_initialized = True
        return True

# --- Sidebar Configuration ---
with st.sidebar:
    st.subheader("⚙️ System Settings")
    
    # Model selection
    available_models = []
    has_openai_key = os.environ.get("OPENAI_API_KEY") is not None
    if has_openai_key:
        available_models.extend(["gpt-4o-mini", "gpt-4o"])
    
    if not available_models:
        st.warning("⚠️ OPENAI_API_KEY is not configured.")
        available_models = ["gpt-4o-mini"]
    
    previous_model = st.session_state.selected_model
    st.session_state.selected_model = st.selectbox(
        "🤖 Select model to use",
        options=available_models,
        index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
    )
    
    if previous_model != st.session_state.selected_model and st.session_state.session_initialized:
        st.warning("⚠️ Model has been changed. Click 'Apply Settings' to apply changes.")
    
    # Timeout setting
    st.session_state.timeout_seconds = st.slider(
        "⏱️ Response generation time limit (seconds)",
        min_value=60,
        max_value=300,
        value=st.session_state.timeout_seconds,
        step=10
    )
    
    st.session_state.recursion_limit = st.slider(
        "⏱️ Recursion call limit (count)",
        min_value=10,
        max_value=200,
        value=st.session_state.recursion_limit,
        step=10
    )
    
    st.divider()
    
    # Tool settings
    st.subheader("🔧 Tool Settings")
    
    if "mcp_tools_expander" not in st.session_state:
        st.session_state.mcp_tools_expander = False
    
    with st.expander("🧰 Add MCP Tools", expanded=st.session_state.mcp_tools_expander):
        loaded_config = load_config_from_json()
        
        if "pending_mcp_config" not in st.session_state:
            st.session_state.pending_mcp_config = loaded_config
        
        st.subheader("Add Tool (JSON format)")
        st.markdown("Please insert **ONE tool** in JSON format.")
        
        example_json = {
            "spotify_search": {
                "command": "python",
                "args": ["./mcp_server_spotify.py"],
                "transport": "stdio"
            }
        }
        
        default_text = json.dumps(example_json, indent=2, ensure_ascii=False)
        new_tool_json = st.text_area("Tool JSON", default_text, height=250)
        
        if st.button("Add Tool", type="primary", key="add_tool_button", use_container_width=True):
            try:
                if not new_tool_json.strip().startswith("{") or not new_tool_json.strip().endswith("}"):
                    st.error("JSON must start and end with curly braces ({}).")
                else:
                    parsed_tool = json.loads(new_tool_json)
                    
                    if "mcpServers" in parsed_tool:
                        parsed_tool = parsed_tool["mcpServers"]
                        st.info("'mcpServers' format detected. Converting automatically.")
                    
                    if len(parsed_tool) == 0:
                        st.error("Please enter at least one tool.")
                    else:
                        success_tools = []
                        for tool_name, tool_config in parsed_tool.items():
                            if "url" in tool_config:
                                tool_config["transport"] = "sse"
                                st.info(f"URL detected in '{tool_name}' tool, setting transport to 'sse'.")
                            elif "transport" not in tool_config:
                                tool_config["transport"] = "stdio"
                            
                            if ("command" not in tool_config and "url" not in tool_config):
                                st.error(f"'{tool_name}' tool configuration requires either 'command' or 'url' field.")
                            elif "command" in tool_config and "args" not in tool_config:
                                st.error(f"'{tool_name}' tool configuration requires 'args' field.")
                            elif "command" in tool_config and not isinstance(tool_config["args"], list):
                                st.error(f"'args' field in '{tool_name}' tool must be an array ([]) format.")
                            else:
                                st.session_state.pending_mcp_config[tool_name] = tool_config
                                success_tools.append(tool_name)
                        
                        if success_tools:
                            if len(success_tools) == 1:
                                st.success(f"{success_tools[0]} tool has been added. Click 'Apply Settings' to apply.")
                            else:
                                tool_names = ", ".join(success_tools)
                                st.success(f"Total {len(success_tools)} tools ({tool_names}) have been added. Click 'Apply Settings' to apply.")
                            st.session_state.mcp_tools_expander = False
                            st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"JSON parsing error: {e}")
            except Exception as e:
                st.error(f"Error occurred: {e}")
    
    # Display registered tools
    with st.expander("📋 Registered Tools List", expanded=True):
        try:
            pending_config = st.session_state.pending_mcp_config
        except Exception as e:
            st.error("Not a valid MCP tool configuration.")
        else:
            for tool_name in list(pending_config.keys()):
                col1, col2 = st.columns([8, 2])
                col1.markdown(f"- **{tool_name}**")
                if col2.button("Delete", key=f"delete_{tool_name}"):
                    del st.session_state.pending_mcp_config[tool_name]
                    st.success(f"{tool_name} tool has been deleted. Click 'Apply Settings' to apply.")
    
    st.divider()
    
    # System Information
    st.subheader("📊 System Information")
    st.write(f"🛠️ MCP Tools Count: {st.session_state.get('tool_count', 'Initializing...')}")
    st.write(f"🧠 Current Model: {st.session_state.selected_model}")
    
    # Environment Variables Check
    st.subheader("🔑 Environment Variables")
    
    # Check required API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    spotify_client_id = os.environ.get("SPOTIFY_USER_ID")
    spotify_client_secret = os.environ.get("SPOTIFY_TOKEN")
    hotpepper_key = os.environ.get("HOTPEPPER_API_KEY")
    google_maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if openai_key:
        st.success("✅ OPENAI_API_KEY: Configured")
    else:
        st.error("❌ OPENAI_API_KEY: Not configured")
    
    if spotify_client_id and spotify_client_secret:
        st.success("✅ Spotify API: Configured")
    else:
        st.warning("⚠️ Spotify API: Not configured (SPOTIFY_USER_ID, SPOTIFY_TOKEN)")
    
    if hotpepper_key:
        st.success("✅ HotPepper API: Configured")
    else:
        st.warning("⚠️ HotPepper API: Not configured (HOTPEPPER_API_KEY)")
    
    if google_maps_key:
        st.success("✅ Google Maps API: Configured")
    else:
        st.warning("⚠️ Google Maps API: Not configured (GOOGLE_MAPS_API_KEY)")
    
    # Apply Settings button
    if st.button("Apply Settings", key="apply_button", type="primary", use_container_width=True):
        # Display applying message
        apply_status = st.empty()
        with apply_status.container():
            st.warning("🔄 Applying changes. Please wait...")
            progress_bar = st.progress(0)

            # Save settings
            st.session_state.mcp_config_text = json.dumps(
                st.session_state.pending_mcp_config, indent=2, ensure_ascii=False
            )

            # Save settings to config.json file
            save_result = save_config_to_json(st.session_state.pending_mcp_config)
            if not save_result:
                st.error("❌ Failed to save settings file.")
            
            progress_bar.progress(15)

            # Prepare session initialization
            st.session_state.session_initialized = False
            st.session_state.agent = None

            # Update progress
            progress_bar.progress(30)
            
            # Run initialization
            success = st.session_state.event_loop.run_until_complete(
                initialize_session(st.session_state.pending_mcp_config)
            )

            # Update progress
            progress_bar.progress(100)
            
            if success:
                st.success("✅ New settings have been applied.")
                # Collapse tool addition expander
                if "mcp_tools_expander" in st.session_state:
                    st.session_state.mcp_tools_expander = False
            else:
                st.error("❌ Failed to apply settings.")

        # Refresh page
        st.rerun()
    
    st.divider()
    
    # Actions
    st.subheader("🔄 Actions")
    
    if st.button("Reset Conversation", use_container_width=True, type="primary"):
        st.session_state.thread_id = random_uuid()
        st.session_state.history = []
        st.success("✅ Conversation has been reset.")
        st.rerun()
    
    if use_login and st.session_state.authenticated:
        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.success("✅ You have been logged out.")
            st.rerun()

# --- Main Application Tabs ---
tab1, tab2, tab3 = st.tabs(["🎵 Music Search", "🍽️ Restaurant Search", "💬 Chat Agent"])

# Music Search Tab
with tab1:
    st.header("🎵 Spotify Music Search")
    
    with st.form("music_search_form"):
        music_query = st.text_input("検索したい楽曲名またはアーティスト名", "夜に駆ける")
        music_submitted = st.form_submit_button("検索")
    
    if music_submitted:
        with st.spinner("Spotifyで検索中..."):
            # Tool関数を直接呼び出す代わりに、通常の関数として呼び出す
            result = search_spotify_tracks_func(music_query)
        
        if 'error' in result:
            st.error(f"エラー: {result['error']}")
        else:
            tracks = result.get('tracks', [])
            st.success(result.get('message', f"{len(tracks)}件見つかりました。"))
            
            if tracks:
                st.subheader("🎵 検索結果（上位10件）")
                
                # 統計情報を表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総件数", len(tracks))
                with col2:
                    avg_popularity = sum(track.get('popularity', 0) for track in tracks) / len(tracks) if tracks else 0
                    st.metric("平均人気度", f"{avg_popularity:.1f}")
                with col3:
                    unique_artists = len(set(track.get('artist', '') for track in tracks))
                    st.metric("アーティスト数", unique_artists)
                
                st.divider()
                
                for i, track in enumerate(tracks[:10], 1):
                    # メイン情報とSpotify埋め込みを横に並べる
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # 楽曲情報
                        st.markdown(f"### {i}. {track['name']}")
                        
                        # 基本情報
                        info_cols = st.columns(2)
                        with info_cols[0]:
                            st.markdown(f"🎤 **アーティスト**: {track['artist']}")
                            st.markdown(f"💿 **アルバム**: {track['album']}")
                        
                        with info_cols[1]:
                            popularity = track.get('popularity', 0)
                            # 人気度を星で表示
                            stars = "⭐" * (popularity // 20) + "☆" * (5 - popularity // 20)
                            st.markdown(f"⭐ **人気度**: {stars} ({popularity})")
                            
                            # 再生時間を分:秒形式で表示
                            duration_seconds = track.get('duration_ms', 0) // 1000
                            duration_min = duration_seconds // 60
                            duration_sec = duration_seconds % 60
                            st.markdown(f"⏱️ **再生時間**: {duration_min}:{duration_sec:02d}")
                        
                        # リンクボタン
                        if track.get('spotify_url'):
                            st.markdown(f"[🎵 Spotifyで聴く]({track['spotify_url']})")
                    
                    with col2:
                        # Spotify埋め込みプレイヤー
                        url = track.get('spotify_url')
                        if url and 'track/' in url:
                            track_id = url.split('track/')[-1].split('?')[0]
                            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                            st.markdown(
                                f'''
                                <div class="spotify-embed-container" style="
                                    border-radius: 12px; 
                                    overflow: hidden; 
                                    width: 100%; 
                                    height: 152px;
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    border: 1px solid #e0e0e0;
                                    background: #191414;
                                ">
                                    <iframe 
                                        src="{embed_url}" 
                                        width="100%" 
                                        height="152" 
                                        frameborder="0" 
                                        allowtransparency="true" 
                                        allow="encrypted-media"
                                        loading="lazy"
                                    ></iframe>
                                </div>
                                ''',
                                unsafe_allow_html=True
                            )
                        else:
                            st.info("🎵 Spotify埋め込みが利用できません")
                    
                    # 区切り線
                    if i < len(tracks[:10]):
                        st.divider()
            else:
                st.warning("該当する楽曲が見つかりませんでした。")

# Restaurant Search Tab
with tab2:
    st.header("🍽️ Restaurant Search (HotPepper + Google Maps)")
    
    with st.form("restaurant_search_form"):
        location = st.text_input("エリア名 (例: 大崎, 渋谷, 新宿)", "大崎")
        cuisine = st.text_input("ジャンル (例: 居酒屋, イタリアン, 中華)", "")
        budget = st.text_input("予算 (例: 3000円以下)", "")
        restaurant_submitted = st.form_submit_button("検索")
    
    if restaurant_submitted:
        with st.spinner("HotPepper・Google両方から検索中..."):
            # Tool関数を直接呼び出す代わりに、通常の関数として呼び出す
            result = search_restaurants_func(location, cuisine, budget)
        
        if 'error' in result:
            st.error(f"エラー: {result['error']}")
        else:
            restaurants = result.get('restaurants', [])
            st.success(result.get('message', f"{len(restaurants)}件見つかりました。"))
            
            if restaurants:
                st.subheader("🍽️ 検索結果（上位10件）")
                
                # 統計情報を表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総件数", len(restaurants))
                with col2:
                    st.metric("HotPepper", result.get('hotpepper_count', 0))
                with col3:
                    st.metric("Google Maps", result.get('google_maps_count', 0))
                
                st.divider()
                
                for i, restaurant in enumerate(restaurants[:10], 1):
                    # メイン情報と地図を横に並べる
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # レストラン情報
                        st.markdown(f"### {i}. {restaurant['name']}")
                        
                        # 基本情報
                        info_cols = st.columns(2)
                        with info_cols[0]:
                            st.markdown(f"📍 **住所**: {restaurant.get('address', '住所不明')}")
                            if restaurant.get('cuisine'):
                                st.markdown(f"🍴 **ジャンル**: {restaurant['cuisine']}")
                            if restaurant.get('budget'):
                                st.markdown(f"💰 **予算**: {restaurant['budget']}")
                        
                        with info_cols[1]:
                            if restaurant.get('rating') and restaurant['rating'] != '評価なし':
                                st.markdown(f"⭐ **HotPepper評価**: {restaurant['rating']}")
                            if restaurant.get('google_rating'):
                                st.markdown(f"⭐ **Google評価**: {restaurant['google_rating']}")
                            if restaurant.get('price_level'):
                                st.markdown(f"💵 **価格レベル**: {restaurant['price_level']}")
                        
                        # リンクボタン
                        link_cols = st.columns(2)
                        with link_cols[0]:
                            if restaurant.get('url'):
                                st.markdown(f"[🔗 HotPepperで詳細を見る]({restaurant['url']})")
                        with link_cols[1]:
                            if restaurant.get('google_maps_url'):
                                st.markdown(f"[🗺️ Googleマップで見る]({restaurant['google_maps_url']})")
                    
                    with col2:
                        # Googleマップの埋め込みプレビュー
                        if restaurant.get('address') and restaurant['address'] != '住所不明':
                            try:
                                show_googlemap_embed_streamlit(
                                    restaurant['address'], 
                                    title=f"📍 {restaurant['name']}"
                                )
                            except Exception as e:
                                st.info("🗺️ 地図の表示に失敗しました")
                        elif restaurant.get('google_maps_url'):
                            # GoogleマップのURLがある場合は、リンクのみ表示
                            st.markdown(f"[🗺️ Googleマップで場所を確認]({restaurant['google_maps_url']})")
                        else:
                            st.info("🗺️ 住所情報がありません")
                    
                    # 区切り線
                    if i < len(restaurants[:10]):
                        st.divider()
            else:
                st.warning("該当するレストランが見つかりませんでした。")

# --- Chat Agent Functions ---

def get_streaming_callback(text_placeholder, tool_placeholder):
    """Creates a streaming callback function."""
    accumulated_text = []
    accumulated_tool = []

    def callback_func(message: dict):
        nonlocal accumulated_text, accumulated_tool
        message_content = message.get("content", None)

        if isinstance(message_content, AIMessageChunk):
            content = message_content.content
            # If content is in list form (mainly occurs in Claude models)
            if isinstance(content, list) and len(content) > 0:
                message_chunk = content[0]
                # Process text type
                if message_chunk["type"] == "text":
                    accumulated_text.append(message_chunk["text"])
                    text_placeholder.markdown("".join(accumulated_text))
                # Process tool use type
                elif message_chunk["type"] == "tool_use":
                    if "partial_json" in message_chunk:
                        accumulated_tool.append(message_chunk["partial_json"])
                    else:
                        tool_call_chunks = message_content.tool_call_chunks
                        tool_call_chunk = tool_call_chunks[0]
                        accumulated_tool.append(
                            "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                        )
                    with tool_placeholder.expander(
                        "🔧 Tool Call Information", expanded=True
                    ):
                        st.markdown("".join(accumulated_tool))
            # Process if tool_calls attribute exists (mainly occurs in OpenAI models)
            elif (
                hasattr(message_content, "tool_calls")
                and message_content.tool_calls
                and len(message_content.tool_calls[0]["name"]) > 0
            ):
                tool_call_info = message_content.tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "🔧 Tool Call Information", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
            # Process if content is a simple string
            elif isinstance(content, str):
                accumulated_text.append(content)
                text_placeholder.markdown("".join(accumulated_text))
            # Process if invalid tool call information exists
            elif (
                hasattr(message_content, "invalid_tool_calls")
                and message_content.invalid_tool_calls
            ):
                tool_call_info = message_content.invalid_tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "🔧 Tool Call Information (Invalid)", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
            # Process if tool_call_chunks attribute exists
            elif (
                hasattr(message_content, "tool_call_chunks")
                and message_content.tool_call_chunks
            ):
                tool_call_chunk = message_content.tool_call_chunks[0]
                accumulated_tool.append(
                    "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                )
                with tool_placeholder.expander(
                    "🔧 Tool Call Information", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
            # Process if tool_calls exists in additional_kwargs (supports various model compatibility)
            elif (
                hasattr(message_content, "additional_kwargs")
                and "tool_calls" in message_content.additional_kwargs
            ):
                tool_call_info = message_content.additional_kwargs["tool_calls"][0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "🔧 Tool Call Information", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
        # Process if it's a tool message (tool response)
        elif isinstance(message_content, ToolMessage):
            accumulated_tool.append(
                "\n```json\n" + str(message_content.content) + "\n```\n"
            )
            with tool_placeholder.expander("🔧 Tool Call Information", expanded=True):
                st.markdown("".join(accumulated_tool))
        return None

    return callback_func, accumulated_text, accumulated_tool

async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=60):
    """Processes user questions and generates responses."""
    try:
        if st.session_state.agent:
            streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
                get_streaming_callback(text_placeholder, tool_placeholder)
            )
            try:
                response = await asyncio.wait_for(
                    astream_graph(
                        st.session_state.agent,
                        {"messages": [HumanMessage(content=query)]},
                        callback=streaming_callback,
                        config=RunnableConfig(
                            recursion_limit=st.session_state.recursion_limit,
                            thread_id=st.session_state.thread_id,
                        ),
                    ),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                error_msg = f"⏱️ Request time exceeded {timeout_seconds} seconds. Please try again later."
                return {"error": error_msg}, error_msg, ""

            final_text = "".join(accumulated_text_obj)
            final_tool = "".join(accumulated_tool_obj)
            return response, final_text, final_tool
        else:
            return (
                {"error": "🚫 Agent has not been initialized."},
                "🚫 Agent has not been initialized.",
                "",
            )
    except Exception as e:
        import traceback

        error_msg = f"❌ Error occurred during query processing: {str(e)}\n{traceback.format_exc()}"
        return {"error": error_msg}, error_msg, ""

def print_message():
    """Displays chat history on the screen."""
    i = 0
    while i < len(st.session_state.history):
        message = st.session_state.history[i]

        if message["role"] == "user":
            st.chat_message("user", avatar="🧑‍💻").markdown(message["content"])
            i += 1
        elif message["role"] == "assistant":
            # Create assistant message container
            with st.chat_message("assistant", avatar="🤖"):
                # Display assistant message content
                st.markdown(message["content"])

                # Check if the next message is tool call information
                if (
                    i + 1 < len(st.session_state.history)
                    and st.session_state.history[i + 1]["role"] == "assistant_tool"
                ):
                    # Display tool call information in the same container as an expander
                    with st.expander("🔧 Tool Call Information", expanded=False):
                        st.markdown(st.session_state.history[i + 1]["content"])
                    i += 2  # Increment by 2 as we processed two messages together
                else:
                    i += 1  # Increment by 1 as we only processed a regular message
        else:
            # Skip assistant_tool messages as they are handled above
            i += 1

# Chat Agent Tab
with tab3:
    st.header("💬 Chat Agent")
    
    # Initialize default session (if not initialized)
    if not st.session_state.session_initialized:
        st.info(
            "MCP server and agent are not initialized. Please click the 'Apply Settings' button in the left sidebar to initialize."
        )
        
        # デバッグ情報を表示
        with st.expander("🔍 Debug Information", expanded=False):
            st.write(f"**Session Initialized**: {st.session_state.session_initialized}")
            st.write(f"**Agent**: {st.session_state.agent is not None}")
            st.write(f"**MCP Client**: {st.session_state.mcp_client is not None}")
            st.write(f"**Tool Count**: {st.session_state.get('tool_count', 'Not set')}")
            st.write(f"**Selected Model**: {st.session_state.selected_model}")
            
            # 環境変数の確認
            st.write("**Environment Variables**:")
            openai_key = os.environ.get("OPENAI_API_KEY")
            st.write(f"  - OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
            
            # 設定ファイルの確認
            st.write("**Configuration**:")
            try:
                config = load_config_from_json()
                st.write(f"  - Config loaded: ✅ ({len(config)} tools)")
                for tool_name, tool_config in config.items():
                    st.write(f"    - {tool_name}: {tool_config.get('command', 'N/A')}")
            except Exception as e:
                st.write(f"  - Config error: ❌ {str(e)}")
    else:
        # 初期化済みの場合の情報表示
        st.success("✅ Chat Agent is ready to use!")
        with st.expander("🔍 Agent Status", expanded=False):
            st.write(f"**Tool Count**: {st.session_state.get('tool_count', 'Unknown')}")
            st.write(f"**Model**: {st.session_state.selected_model}")
            st.write(f"**Timeout**: {st.session_state.timeout_seconds} seconds")
            st.write(f"**Recursion Limit**: {st.session_state.recursion_limit}")
    
    # Print conversation history
    print_message()
    
    # User input and processing
    user_query = st.chat_input("💬 Enter your question")
    if user_query:
        if st.session_state.session_initialized:
            st.chat_message("user", avatar="🧑‍💻").markdown(user_query)
            with st.chat_message("assistant", avatar="🤖"):
                tool_placeholder = st.empty()
                text_placeholder = st.empty()
                resp, final_text, final_tool = (
                    st.session_state.event_loop.run_until_complete(
                        process_query(
                            user_query,
                            text_placeholder,
                            tool_placeholder,
                            st.session_state.timeout_seconds,
                        )
                    )
                )
            if "error" in resp:
                st.error(resp["error"])
            else:
                # 音楽検索の特別処理（ストリーミング完了後）
                if "search_spotify_tracks_tool" in final_tool:
                    try:
                        # ツール呼び出し情報から検索クエリを抽出
                        import re
                        tool_call_match = re.search(r'"query":\s*"([^"]+)"', final_tool)
                        if tool_call_match:
                            extracted_query = tool_call_match.group(1)
                            
                            # 抽出したクエリで再検索して可視化
                            st.markdown("---")
                            st.markdown("### 🎵 Spotify検索結果")
                            
                            with st.spinner(f"🎵 '{extracted_query}' を検索中..."):
                                result = search_spotify_tracks_func(extracted_query)
                            
                            if 'error' in result:
                                st.error(f"エラー: {result['error']}")
                            else:
                                tracks = result.get('tracks', [])
                                st.success(result.get('message', f"{len(tracks)}件見つかりました。"))
                                
                                if tracks:
                                    st.subheader("🎵 検索結果（上位10件）")
                                    
                                    # 統計情報を表示
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("総件数", len(tracks))
                                    with col2:
                                        avg_popularity = sum(track.get('popularity', 0) for track in tracks) / len(tracks) if tracks else 0
                                        st.metric("平均人気度", f"{avg_popularity:.1f}")
                                    with col3:
                                        unique_artists = len(set(track.get('artist', '') for track in tracks))
                                        st.metric("アーティスト数", unique_artists)
                                    
                                    st.divider()
                                    
                                    for i, track in enumerate(tracks[:10], 1):
                                        # 楽曲情報とSpotify埋め込みプレイヤーを横に並べる
                                        col1, col2 = st.columns([2, 1])
                                        
                                        with col1:
                                            # 楽曲情報
                                            st.markdown(f"### {i}. {track['name']}")
                                            
                                            # 基本情報
                                            info_cols = st.columns(2)
                                            with info_cols[0]:
                                                st.markdown(f"🎤 **アーティスト**: {track['artist']}")
                                                st.markdown(f"💿 **アルバム**: {track['album']}")
                                            
                                            with info_cols[1]:
                                                popularity = track.get('popularity', 0)
                                                # 人気度を星で表示
                                                stars = "⭐" * (popularity // 20) + "☆" * (5 - popularity // 20)
                                                st.markdown(f"⭐ **人気度**: {stars} ({popularity})")
                                                
                                                # 再生時間を分:秒形式で表示
                                                duration_seconds = track.get('duration_ms', 0) // 1000
                                                duration_min = duration_seconds // 60
                                                duration_sec = duration_seconds % 60
                                                st.markdown(f"⏱️ **再生時間**: {duration_min}:{duration_sec:02d}")
                                            
                                            # Spotifyリンク（クリックして再生）
                                            if track.get('spotify_url'):
                                                st.markdown(f"🎵 **[Spotifyで聴く]({track['spotify_url']})**")
                                        
                                        with col2:
                                            # Spotify埋め込みプレイヤー
                                            url = track.get('spotify_url')
                                            if url and 'track/' in url:
                                                track_id = url.split('track/')[-1].split('?')[0]
                                                embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                                                st.markdown(
                                                    f'''
                                                    <div class="spotify-embed-container" style="
                                                        border-radius: 12px; 
                                                        overflow: hidden; 
                                                        width: 100%; 
                                                        height: 152px;
                                                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                                        border: 1px solid #e0e0e0;
                                                        background: #191414;
                                                    ">
                                                        <iframe 
                                                            src="{embed_url}" 
                                                            width="100%" 
                                                            height="152" 
                                                            frameborder="0" 
                                                            allowtransparency="true" 
                                                            allow="encrypted-media"
                                                            loading="lazy"
                                                        ></iframe>
                                                    </div>
                                                    ''',
                                                    unsafe_allow_html=True
                                                )
                                            else:
                                                st.info("🎵 Spotify埋め込みが利用できません")
                                        
                                        # 区切り線
                                        if i < len(tracks[:10]):
                                            st.divider()
                                else:
                                    st.warning("該当する楽曲が見つかりませんでした。")
                    except Exception as e:
                        st.error(f"音楽検索の処理中にエラーが発生しました: {str(e)}")
                
                st.session_state.history.append({"role": "user", "content": user_query})
                st.session_state.history.append(
                    {"role": "assistant", "content": final_text}
                )
                if final_tool.strip():
                    st.session_state.history.append(
                        {"role": "assistant_tool", "content": final_tool}
                    )
                st.rerun()
        else:
            st.warning(
                "⚠️ MCP server and agent are not initialized. Please click the 'Apply Settings' button in the left sidebar to initialize."
            )

def process_chat_query(query: str) -> dict:
    """チャットクエリを処理し、適切な機能を呼び出す"""
    query_lower = query.lower()
    
    # 音楽検索のキーワードをチェック
    music_keywords = ['音楽', '楽曲', '曲', '歌', 'アーティスト', 'ミュージック', 'spotify', '音楽を教えて', '曲を教えて']
    if any(keyword in query_lower for keyword in music_keywords):
        # 音楽検索のクエリを抽出
        music_query = extract_music_query(query)
        if music_query:
            return {
                "type": "music",
                "query": music_query,
                "tool_name": "search_tracks",
                "tool_args": {"query": music_query, "limit": 10}
            }
    
    # レストラン検索のキーワードをチェック
    restaurant_keywords = ['レストラン', '食事', 'お店', '店', '食べ', 'ご飯', 'グルメ', 'hotpepper', 'レストランを教えて', 'お店を教えて']
    if any(keyword in query_lower for keyword in restaurant_keywords):
        # レストラン検索のパラメータを抽出
        location, cuisine, budget = extract_restaurant_params(query)
        if location:
            return {
                "type": "restaurant",
                "location": location,
                "cuisine": cuisine,
                "budget": budget,
                "tool_name": "search_restaurants",
                "tool_args": {"location": location, "cuisine": cuisine, "budget": budget, "count": 20}
            }
    
    # その他の質問の場合は一般的な応答
    return {
        "type": "general",
        "message": f"「{query}」についてお答えします。\n\nこのシステムでは以下の機能が利用できます：\n\n🎵 **音楽検索**: 「〇〇の曲を教えて」「〇〇の音楽を検索して」\n🍽️ **レストラン検索**: 「〇〇のレストランを教えて」「〇〇で食事できるお店を探して」\n\n具体的な質問をしていただければ、適切な機能でお答えします。"
    }

def extract_music_query(query: str) -> str:
    """音楽検索クエリを抽出する"""
    # 一般的なパターンを処理
    patterns = [
        r'(.+?)の曲を教えて',
        r'(.+?)の音楽を教えて',
        r'(.+?)の歌を教えて',
        r'(.+?)を検索して',
        r'(.+?)の楽曲を教えて'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1).strip()
    
    # パターンにマッチしない場合は、最後の部分を抽出
    words = query.split()
    if len(words) > 1:
        # 「教えて」「検索して」などの動詞を除く
        filtered_words = [w for w in words if w not in ['教えて', '検索して', 'を', 'の', 'は', 'が']]
        if filtered_words:
            return ' '.join(filtered_words)
    
    return query

def extract_restaurant_params(query: str) -> tuple:
    """レストラン検索パラメータを抽出する"""
    location = ""
    cuisine = ""
    budget = ""
    
    # エリアの抽出
    area_patterns = [
        r'(.+?)のレストラン',
        r'(.+?)で食事',
        r'(.+?)のお店',
        r'(.+?)のグルメ'
    ]
    
    for pattern in area_patterns:
        match = re.search(pattern, query)
        if match:
            location = match.group(1).strip()
            break
    
    # ジャンルの抽出
    cuisine_patterns = [
        r'(.+?)料理',
        r'(.+?)レストラン',
        r'(.+?)店'
    ]
    
    for pattern in cuisine_patterns:
        match = re.search(pattern, query)
        if match:
            cuisine = match.group(1).strip()
            break
    
    # 予算の抽出
    budget_patterns = [
        r'(\d+)円以下',
        r'(\d+)円以下',
        r'予算(.+?)円'
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, query)
        if match:
            budget = f"{match.group(1)}円以下"
            break
    
    return location, cuisine, budget