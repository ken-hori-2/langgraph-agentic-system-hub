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

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import multi-agent system
try:
    from supervisor_workers_multiagents import app, run_agent, run_agent_music
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.info("supervisor_workers_multiagents.py file not found.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Agentic AI Multi-Agent Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <h1>🧠 Agentic AI Multi-Agent Assistant</h1>
        <p>Specialized agents handle your diverse requests with intelligent orchestration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✍️ Made by [ken-hori-2](https://github.com/ken-hori-2) 🚀")
        st.markdown("### 💻 [Project Repository](https://github.com/ken-hori-2/work_supervisor)")
        st.divider()
        
        st.markdown("### 🎯 Agent Selection")
        
        # Agent selection
        agent_options = {
            "auto": "🧠 Auto Selection (Recommended)",
            "music": "🎼 Music Expert",
            "video": "🎬 Video Expert", 
            "travel": "🗺️ Travel Expert",
            "restaurant": "🍽️ Restaurant Expert",
            "scheduler": "📅 Scheduler",
            "math": "🔢 Math Expert",
            "research": "🔬 Research Expert"
        }
        
        selected_agent = st.selectbox(
            "Select an agent to use",
            options=list(agent_options.keys()),
            format_func=lambda x: agent_options[x],
            index=0
        )
        
        st.session_state.current_agent = selected_agent
        
        st.divider()
        
        # System settings
        st.markdown("### ⚙️ System Settings")
        
        # Debug mode
        debug_mode = st.checkbox("🐛 Debug Mode", value=False)
        st.session_state.debug_mode = debug_mode
        
        # Latest answer only option
        show_latest_only = st.checkbox("🎯 Show Latest Answer Only", value=False)
        st.session_state.show_latest_only = show_latest_only
        
        st.divider()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎼 Music", key="quick_music", use_container_width=True):
                st.session_state.current_agent = "music"
                st.session_state.quick_action = "music"
                st.rerun()
                
        with col2:
            if st.button("🍽️ Restaurant", key="quick_restaurant", use_container_width=True):
                st.session_state.current_agent = "restaurant"
                st.session_state.quick_action = "restaurant"
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🗺️ Travel", key="quick_travel", use_container_width=True):
                st.session_state.current_agent = "travel"
                st.session_state.quick_action = "travel"
                st.rerun()
                
        with col4:
            if st.button("🎬 Video", key="quick_video", use_container_width=True):
                st.session_state.current_agent = "video"
                st.session_state.quick_action = "video"
                st.rerun()
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Conversations", len(st.session_state.chat_history))
        with col2:
            st.metric("Avg. Processing Time", f"{st.session_state.get('avg_processing_time', 0):.1f}s")
        
        st.divider()
        
        # Action buttons
        st.markdown("### 🔄 Actions")
        
        # Clear button
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="primary"):
            st.session_state.chat_history = []
            st.success("✅ Chat history cleared.")
            st.rerun()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        analytics_interface()
    
    with tab3:
        settings_interface()

def chat_interface():
    # Quick action processing
    if hasattr(st.session_state, 'quick_action'):
        quick_action = st.session_state.quick_action
        del st.session_state.quick_action
        
        if quick_action == "music":
            st.info("🎼 Music Expert Mode. Please enter artist name or song title.")
        elif quick_action == "restaurant":
            st.info("🍽️ Restaurant Expert Mode. Please enter area or cuisine type.")
        elif quick_action == "travel":
            st.info("🗺️ Travel Expert Mode. Please enter destination or dates.")
        elif quick_action == "video":
            st.info("🎬 Video Expert Mode. Please enter video search keywords.")
    
    # Chat history display
    chat_container = st.container()
    
    with chat_container:
        # Debug information display
        if st.session_state.get('debug_mode', False):
            with st.expander("🐛 Debug Information", expanded=False):
                st.write("**Chat History Debug:**")
                st.write(f"History count: {len(st.session_state.chat_history)}")
                for i, msg in enumerate(st.session_state.chat_history):
                    st.write(f"Message {i}: role={msg.get('role')}, content_length={len(msg.get('content', ''))}")
        
        # Latest answer only display option
        if st.session_state.get('show_latest_only', False) and st.session_state.chat_history:
            # Display only the latest AI answer
            latest_ai_message = None
            for msg in reversed(st.session_state.chat_history):
                if msg["role"] == "assistant":
                    latest_ai_message = msg
                    break
            
            if latest_ai_message:
                st.markdown("### 🎯 Latest Answer")
                
                if "results" in latest_ai_message and latest_ai_message["results"]:
                    tab1, tab2 = st.tabs(["🤖 AI Answer", "📊 Detailed Results"])
                    
                    with tab1:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border: 3px solid #a855f7; box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4); color: white;">
                            <strong>🤖 AI:</strong><br>
                            {latest_ai_message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with tab2:
                        display_results(latest_ai_message["results"])
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border: 3px solid #a855f7; box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4); color: white;">
                        <strong>🤖 AI:</strong><br>
                        {latest_ai_message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Display all history
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #2c5282 0%, #1e3a8a 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #3b82f6; color: white;">
                        <strong>👤 You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Determine if it's the last response
                    is_last_response = (i == len(st.session_state.chat_history) - 1)
                    
                    # Debug information display
                    if st.session_state.get('debug_mode', False) and is_last_response:
                        with st.expander("🐛 Latest Answer Debug", expanded=False):
                            st.write(f"**Latest Answer Debug:** content_length={len(message.get('content', ''))}")
                    
                    # AI answer display with tabs
                    if "results" in message and message["results"]:
                        # Display with tabs if results exist
                        if is_last_response:
                            st.markdown("### 🎯 Latest Answer")
                        
                        tab1, tab2 = st.tabs(["🤖 AI Answer", "📊 Detailed Results"])
                        
                        with tab1:
                            if is_last_response:
                                message_style = "background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%); border: 3px solid #a855f7; box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4);"
                            else:
                                message_style = "background: linear-gradient(135deg, #553c9a 0%, #6b46c1 100%); border-left: 5px solid #a855f7;"
                            
                            st.markdown(f"""
                            <div style="{message_style} padding: 1.5rem; border-radius: 15px; margin: 1rem 0; color: white;">
                                <strong>🤖 AI:</strong><br>
                                {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with tab2:
                            display_results(message["results"])
                    else:
                        # Normal display if no results
                        if is_last_response:
                            st.markdown("### 🎯 Latest Answer")
                            message_style = "background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%); border: 3px solid #a855f7; box-shadow: 0 8px 25px rgba(168, 85, 247, 0.4);"
                        else:
                            message_style = "background: linear-gradient(135deg, #553c9a 0%, #6b46c1 100%); border-left: 5px solid #a855f7;"
                        
                        st.markdown(f"""
                        <div style="{message_style} padding: 1.5rem; border-radius: 15px; margin: 1rem 0; color: white;">
                            <strong>🤖 AI:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input form
    st.markdown("---")
    
    # Input area
    user_input = st.text_area(
        "Enter your message",
        placeholder="Example: Find Italian restaurants in Shibuya, schedule a meeting for tomorrow at 3 PM, tell me about Beatles songs...",
        height=100,
        key=f"user_input_{len(st.session_state.chat_history)}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Send", type="primary", disabled=st.session_state.processing, use_container_width=True):
            if user_input.strip():
                process_user_input(user_input)
                # Update chat history to clear text area
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset", disabled=st.session_state.processing, use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ Chat history reset.")
            st.rerun()
    
    with col3:
        if st.session_state.processing:
            st.info("🔄 Processing...")
        
        # Test button
        if st.button("🧪 Test Answer", disabled=st.session_state.processing, use_container_width=True):
            test_response = "This is a test answer. Testing if AI responses display correctly."
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": test_response,
                "results": [],
                "timestamp": datetime.now()
            })
            st.success("✅ Test answer added.")
            st.rerun()

def process_user_input(user_input):
    st.session_state.processing = True
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🤖 AI Agent is processing...")
        progress_bar.progress(25)
        
        start_time = time.time()
        
        # Agent execution
        try:
            if st.session_state.current_agent == "auto":
                result = run_agent([{"role": "user", "content": user_input}])
            else:
                # Specific agent specified
                result = run_agent([{"role": "user", "content": user_input}])
        except Exception as agent_error:
            st.warning(f"Agent execution error: {str(agent_error)}")
            # Fallback: generate simple response
            result = {
                "text": f"Sorry. There is currently an issue with the agent system.\n\nRequest: {user_input}\n\nError: {str(agent_error)}\n\nPlease try again later.",
                "results": []
            }
        
        processing_time = time.time() - start_time
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Add result to history
        response_text = result.get("text", "Could not generate answer.")
        response_results = result.get("results", [])
        
        # Debug information display (development only)
        if st.session_state.get('debug_mode', False):
            st.write("**Debug Information:**")
            st.write(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            st.write(f"Response text: {response_text}")
            st.write(f"Response results: {response_results}")
            st.write(f"Response text type: {type(response_text)}")
            st.write(f"Response text length: {len(response_text) if response_text else 0}")
            
            # Display raw result
            st.write("**Raw Result:**")
            st.json(result)
        
        # Check if result is not empty
        if not response_text or response_text.strip() == "":
            st.error("⚠️ AI answer is empty. Enable debug mode to check details.")
            response_text = "Could not retrieve AI answer. Enable debug mode to check details."
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text,
            "results": response_results,
            "timestamp": datetime.now(),
            "processing_time": processing_time
        })
        
        # Update average processing time
        if 'avg_processing_time' not in st.session_state:
            st.session_state.avg_processing_time = processing_time
        else:
            st.session_state.avg_processing_time = (
                st.session_state.avg_processing_time + processing_time
            ) / 2
        
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"Sorry. An error occurred: {str(e)}\n\nPlease restart the system or try again later.",
            "timestamp": datetime.now()
        })
    finally:
        st.session_state.processing = False
        progress_bar.empty()
        status_text.empty()

def display_results(results):
    """Display results appropriately"""
    if not results:
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
    """Display restaurant results"""
    st.markdown("### 🍽️ Restaurant Search Results")
    
    for i, restaurant in enumerate(restaurants):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #667eea; color: white;">
                    <h4>🍽️ {restaurant.get('name', 'N/A')}</h4>
                    <p><strong>Cuisine:</strong> {restaurant.get('cuisine', 'N/A')}</p>
                    <p><strong>Budget:</strong> {restaurant.get('budget', 'N/A')}</p>
                    <p><strong>Rating:</strong> {restaurant.get('rating', 'N/A')}</p>
                    <p><strong>Address:</strong> {restaurant.get('address', 'N/A')}</p>
                    <p><strong>Hours:</strong> {restaurant.get('hours', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if restaurant.get('google_maps_url'):
                    st.markdown(f"""
                    <a href="{restaurant['google_maps_url']}" target="_blank">
                        <button style="background: #4285f4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            🗺️ Google Maps
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                
                if restaurant.get('directions_url'):
                    st.markdown(f"""
                    <a href="{restaurant['directions_url']}" target="_blank">
                        <button style="background: #34a853; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            🚇 Directions
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_hotel_results(hotels):
    """Display hotel results"""
    st.markdown("### 🏨 Hotel Search Results")
    
    for i, hotel in enumerate(hotels):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #667eea; color: white;">
                    <h4>🏨 {hotel.get('name', 'N/A')}</h4>
                    <p><strong>Price:</strong> {hotel.get('price', 'N/A')}</p>
                    <p><strong>Rating:</strong> {hotel.get('rating', 'N/A')}</p>
                    <p><strong>Amenities:</strong> {', '.join(hotel.get('amenities', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if hotel.get('url'):
                    st.markdown(f"""
                    <a href="{hotel['url']}" target="_blank">
                        <button style="background: #ff6b6b; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            📖 View Details
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_video_results(videos):
    """Display video results"""
    st.markdown("### 📹 Video Search Results")
    
    for i, video in enumerate(videos):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if video.get('thumbnail'):
                    st.image(video['thumbnail'], width=200)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #667eea; color: white;">
                    <h4>📹 {video.get('title', 'N/A')}</h4>
                    <p><strong>Channel:</strong> {video.get('channel', 'N/A')}</p>
                    <p><strong>Description:</strong> {video.get('description', 'N/A')[:100]}...</p>
                    <p><strong>Published:</strong> {video.get('published_at', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if video.get('youtube_url'):
                    st.markdown(f"""
                    <a href="{video['youtube_url']}" target="_blank">
                        <button style="background: #ff0000; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                            ▶️ Watch on YouTube
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

def display_spotify_results(tracks):
    """Display Spotify results"""
    st.markdown("### 🎵 Music Search Results")
    
    for i, track in enumerate(tracks):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if track.get('album_art'):
                    st.image(track['album_art'], width=150)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #667eea; color: white;">
                    <h4>🎵 {track.get('name', 'N/A')}</h4>
                    <p><strong>Artist:</strong> {track.get('artist', 'N/A')}</p>
                    <p><strong>Album:</strong> {track.get('album', 'N/A')}</p>
                    <p><strong>Release Date:</strong> {track.get('release_date', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if track.get('spotify_url'):
                    # Spotify embed player
                    track_id = track['spotify_url'].split('track/')[-1].split('?')[0]
                    embed_url = f"https://open.spotify.com/embed/track/{track_id}"
                    st.markdown(f"""
                    <div style="border-radius: 15px; overflow: hidden; margin: 1rem 0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
                        <iframe src="{embed_url}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    </div>
                    """, unsafe_allow_html=True)

def analytics_interface():
    """Analytics interface"""
    st.markdown("## 📊 Analytics Dashboard")
    
    if not st.session_state.chat_history:
        st.info("No chat history. Please start a chat first.")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); border: 2px solid #4a5568; color: white;">
            <h3>📈 Total Messages</h3>
            <h2>{}</h2>
        </div>
        """.format(len(st.session_state.chat_history)), unsafe_allow_html=True)
    
    with col2:
        user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); border: 2px solid #4a5568; color: white;">
            <h3>👤 User Messages</h3>
            <h2>{}</h2>
        </div>
        """.format(len(user_messages)), unsafe_allow_html=True)
    
    with col3:
        assistant_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "assistant"]
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); border: 2px solid #4a5568; color: white;">
            <h3>🤖 AI Answers</h3>
            <h2>{}</h2>
        </div>
        """.format(len(assistant_messages)), unsafe_allow_html=True)
    
    with col4:
        avg_time = st.session_state.get('avg_processing_time', 0)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a1a2e 100%); padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); border: 2px solid #4a5568; color: white;">
            <h3>⏱️ Avg. Processing Time</h3>
            <h2>{:.1f}s</h2>
        </div>
        """.format(avg_time), unsafe_allow_html=True)
    
    st.divider()
    
    # Time series graph
    st.markdown("### 📈 Message Time Series")
    
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
                     title='Message Length Time Series',
                     color_discrete_map={'user': '#2196f3', 'assistant': '#9c27b0'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Processing time distribution
    processing_times = [
        msg.get('processing_time', 0) 
        for msg in st.session_state.chat_history 
        if msg["role"] == "assistant" and msg.get('processing_time')
    ]
    
    if processing_times:
        st.markdown("### ⏱️ Processing Time Distribution")
        fig = px.histogram(x=processing_times, title='Processing Time Distribution',
                          labels={'x': 'Processing Time (seconds)', 'y': 'Frequency'},
                          color_discrete_sequence=['#667eea'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)

def settings_interface():
    """Settings interface"""
    st.markdown("## ⚙️ Settings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔧 Application Settings")
        
        # Theme setting
        theme = st.selectbox(
            "Theme",
            ["dark", "light"],
            index=0
        )
        
        # Language setting
        language = st.selectbox(
            "Language",
            ["English", "日本語"],
            index=0
        )
        
        # Auto-save setting
        auto_save = st.checkbox("Auto-save chat history", value=True)
        
        # Notification setting
        notifications = st.checkbox("Notify on completion", value=True)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.success("✅ Settings saved.")
    
    with col2:
        st.markdown("### 📊 Agent Information")
        
        agents_info = {
            "music": "🎼 Music Expert - Spotify search, playlist retrieval",
            "video": "🎬 Video Expert - YouTube search, video information",
            "travel": "🗺️ Travel Expert - Hotel & Airbnb search",
            "restaurant": "🍽️ Restaurant Expert - Restaurant search & booking",
            "scheduler": "📅 Scheduler - Google Calendar management",
            "math": "🔢 Math Expert - Calculations & formulas",
            "research": "🔬 Research Expert - Web search & information gathering"
        }
        
        for agent, description in agents_info.items():
            st.info(description)
    
    st.divider()
    
    st.markdown("### 🔑 API Settings")
    st.info("API settings are managed in the .env file.")
    
    # API settings confirmation
    with st.expander("🔍 API Settings Check", expanded=False):
        api_keys = {
            "OpenAI API Key": os.environ.get("OPENAI_API_KEY", "Not set"),
            "Anthropic API Key": os.environ.get("ANTHROPIC_API_KEY", "Not set"),
            "Google Maps API Key": os.environ.get("GOOGLE_MAPS_API_KEY", "Not set"),
            "Spotify Client ID": os.environ.get("SPOTIFY_USER_ID", "Not set"),
            "Recruit API Key": os.environ.get("RECRUIT_API_KEY", "Not set")
        }
        
        for key_name, key_value in api_keys.items():
            if key_value != "Not set":
                st.success(f"✅ {key_name}: Set")
            else:
                st.warning(f"⚠️ {key_name}: Not set")

if __name__ == "__main__":
    main() 