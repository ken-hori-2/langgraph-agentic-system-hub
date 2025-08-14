# 🚀 LangGraph Agentic System Hub

> **Integrated AI Agent System** - Multi-Agent Multi-Interface Framework using LangGraph and MCP Tools

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-teal.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--5--sonnet-teal.svg)](https://anthropic.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude--3--7--sonnet-indigo.svg)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [🎯 Overview](#overview)
- [🏗️ System Architecture](#system-architecture)
- [🔧 Component Details](#component-details)
- [🤖 Multi-Agent System](#multi-agent-system)
- [⚙️ Setup](#setup)
- [🎮 Usage](#usage)
- [🔌 API Integration](#api-integration)
- [🔧 Troubleshooting](#troubleshooting)
- [📝 License](#license)

## 🎯 Overview

LangGraph Agentic System Hub provides a **LangGraph-based agentic architecture** that integrates **MCP (Model Context Protocol)** tools to enable intelligent and dynamic task execution in an integrated system.

### 🌟 Key Features

- **🤖 Multi-Agent**: 7 specialized agents working in coordination
- **💻 Multi-Interface**: CLI, GUI, API, MCP integration
- **🔧 Modular Design**: Extensible and reusable components
- **🎯 Specialized Domains**: Each agent specializes in specific tasks
- **🔄 Automatic Routing**: Supervisor automatically selects optimal agents
- **🤖 Multi-Model Support**: OpenAI GPT-4o, Anthropic Claude-3 series support

## 🎥 Demo Video

<div align="center">

**🎬 Multi-Agent System Demo**

> Due to video length constraints, we've split it into two videos, but the app can handle each use case without switching applications.  
> The UI differs between English and Japanese versions for clarity and because it's still in development.

*Watch how multiple specialized agents collaborate to perform music search, restaurant search, schedule management, and more.*

---

### 📹 Demo Video 1: Izakaya Search × Music Recommendation

> **"Asking about izakaya and music tracks, where the supervisor distributes tasks to specialist agents and then generates a comprehensive response"**

https://github.com/user-attachments/assets/90717585-5e53-492d-a558-035fe871605c

*In this demo, when a user asks "Find a stylish izakaya in Shibuya and tell me about Mrs. GREEN APPLE songs", the Restaurant Agent, Music Agent, and others collaborate to generate a response.*

---

### 📹 Demo Video 2: Video Search × Weather Information

> **"Asking about video content and weather, where the supervisor distributes tasks to specialist agents and generates responses"**

https://github.com/user-attachments/assets/d4fe73d3-727b-487c-9826-a6a18e4b2a79

*In this demo, when a user asks "Find English study video content and tell me tomorrow's weather", the Video Agent, Weather Agent, and others collaborate to generate a response.*

---

### 🎞️ Lightweight Demo (GIF)

<!-- Lightweight version (GIF) - Compatibility focused -->
![Demo Animation](./src/langgraph-supervisor/assets/demo_en.gif)
![Demo Animation](./src/langgraph-supervisor/assets/demo_ja.gif)

*Lightweight demo animations. Provided in GIF format for better browser compatibility.*

<!-- Old video links (hidden) -->
<!-- https://github.com/ken-hori-2/langgraph-agentic-system-hub/src/langgraph-supervisor/assets/demo_en.mp4
https://github.com/ken-hori-2/langgraph-agentic-system-hub/src/langgraph-supervisor/assets/demo_ja.mp4 -->

</div>

### 🌐 Web Application

Experience the multi-agent system's web interface:

![Multi-Agent Web Application](./src/langgraph-supervisor/assets/web_gui.png)

#### 🚀 How to Launch

```bash
# Navigate to GUI directory
cd src/langgraph-supervisor/gui

# Launch Japanese version
streamlit run streamlit_app.py

# Launch English version
streamlit run streamlit_app_en.py

# Launch with specific port (e.g., 8501)
streamlit run streamlit_app.py --server.port 8501

# Launch with external access
streamlit run streamlit_app.py --server.address 0.0.0.0
```

#### ✨ Main Features

- **🤖 7 Specialized Agents**: Automatic or manual selection
- **💬 Real-time Chat**: Natural conversation interface
- **📊 Result Visualization**: Restaurant, music, video search results
- **🎯 Quick Actions**: One-click agent switching
- **📈 Analytics**: Conversation history and performance analysis
- **⚙️ Debug Mode**: Detailed processing information

#### 🎯 Usage Example

```
User: "Find an Italian restaurant in Shibuya and tell me about Beatles songs"
→ System: Automatically selects Restaurant Agent and Music Agent
→ Result: Restaurant information + Spotify embedded player
```

## 🏗️ System Architecture

This repository consists of **4 main components**:

### 📁 Project Structure

```
langgraph-agentic-system-hub/
├── 📁 src/
│   ├── 📁 simple-agent-mcp/           # Simple ReAct Agent
│   │   ├── planner_agent.py          # Main agent
│   │   └── 📁 tools/                 # MCP server group
│   │       ├── mcp_server_time.py
│   │       ├── mcp_server_search.py
│   │       └── mcp_server_spotify.py
│   │
│   ├── 📁 streamlit-mcp-server-src/   # Streamlit-based MCP server UI
│   │   ├── 📁 mcp_chat/              # MCP chat application
│   │   │   ├── main.py               # Main execution file
│   │   │   ├── app.py                # Basic application
│   │   │   ├── config.json           # Configuration file
│   │   │   ├── utils.py              # Utility functions
│   │   │   └── 📁 tools/             # MCP server group
│   │   │       ├── mcp_server_time.py    # Time server
│   │   │       ├── mcp_server_search.py  # Search server
│   │   │       ├── mcp_server_spotify.py # Spotify server
│   │   │       ├── mcp_server_googlemaps.py # Google Maps server
│   │   │       ├── mcp_server_rag.py     # RAG server
│   │   │       └── mcp_server_weather.py # Weather server
│   │   │
│   │   └── 📁 mcp_integration/       # MCP integration application
│   │       ├── app_integrated_main.py # Main execution file
│   │       ├── app.py                # Basic application
│   │       ├── requirements_app_integrated.txt # Dependencies
│   │       ├── README.md             # Detailed documentation
│   │       ├── config.json           # Configuration file
│   │       ├── utils.py              # Utility functions
│   │       └── 📁 tools/             # MCP server group
│   │           ├── mcp_server_time.py    # Time server
│   │           ├── mcp_server_spotify.py # Spotify server
│   │           ├── mcp_server_googlemaps.py # Google Maps server
│   │           ├── mcp_server_hotpepper.py # HotPepper server
│   │           └── mcp_server_search.py  # Search server
│   │
│   ├── 📁 uv-agent-api/               # FastAPI-based agent API
│   │   ├── uv_api_agent.py
│   │   ├── uv_api_main.py
│   │   └── uv_api_client.py
│   │
│   └── 📁 langgraph-supervisor/       # 🆕 Multi-Agent Supervisor
│       ├── 📁 cli/                   # Command line interface
│       │   ├── README.md             # CLI usage guide
│       │   ├── supervisor_workers_multiagents.py
│       │   ├── requirements.txt
│       │   └── architecture.html     # Architecture diagram
│       │
│       ├── 📁 gui/                   # Graphical user interface
│       │   ├── README.md             # GUI usage guide
│       │   ├── streamlit_app.py      # Japanese version main application
│       │   ├── streamlit_app_en.py   # English version main application
│       │   ├── supervisor_workers_multiagents.py
│       │   ├── requirements.txt
│       │   ├── setup.sh              # macOS/Linux setup script
│       │   └── setup.bat             # Windows setup script
│       │
│       ├── 📁 assets/                 # Asset files
│       │   ├── demo_en.mp4           # English demo video
│       │   ├── demo_ja.mp4           # Japanese demo video
│       │   ├── demo_en.gif           # English demo GIF
│       │   ├── demo_ja.gif           # Japanese demo GIF
│       │   ├── demo.mp4              # Integrated demo video
│       │   ├── demo.gif              # Integrated demo GIF
│       │   ├── web_ja.png            # Japanese web app image
│       │   ├── web_en.png            # English web app image
│       │   ├── web_gui.png           # Web app image
│       │   └── workflow.png          # Workflow diagram
│       │
│       ├── README.md                 # Detailed documentation
│       └── LICENSE                   # License file
│
├── 📁 docs/
│   └── architecture.png
├── requirements.txt
└── README.md
```

## 🔧 Component Details

### 1. 🎯 Simple ReAct Agent (`simple-agent-mcp/`)

**Simple ReAct Agent** - Single ReAct agent integrating MCP tools

#### Features
- **MCP Tool Integration**: Integration with multiple MCP servers
- **ReAct Reasoning**: Combination of tool usage and reasoning
- **Simple Interaction**: Direct conversation via command line
- **Basic Features**: Music search, web search, time retrieval

#### Usage Example
```bash
# Start MCP servers
python src/simple-agent-mcp/tools/mcp_server_spotify.py
python src/simple-agent-mcp/tools/mcp_server_search.py
python src/simple-agent-mcp/tools/mcp_server_time.py

# Launch agent
python src/simple-agent-mcp/planner_agent.py
```

### 2. 🌐 Streamlit MCP Server Interface (`streamlit-mcp-server-src/`)

**User-friendly Web Interface** - Integration of MCP tools and ReAct agent

#### Features
- **🎯 ReAct Agent**: Intelligent agent that can use multiple tools
- **🔧 Dynamic Tool Management**: Add and configure MCP tools via web interface
- **🗺️ Google Maps Integration**: Route search, place search, geocoding
- **🔍 Web Search**: Advanced search powered by Tavily search API
- **🎵 Spotify Integration**: Music search and recommendations
- **⏰ Time Services**: Current time for different timezones
- **📚 RAG Support**: Document-based question answering
- **🔐 Authentication System**: Login functionality for secure access
- **💬 Real-time Streaming**: Live response streaming with tool call information

#### Folder Structure
- **📁 mcp_chat/**: MCP chat application (ReAct agent)
- **📁 mcp_integration/**: MCP integration application (integrated features)

#### Usage Example
```bash
# MCP chat application
cd src/streamlit-mcp-server-src/mcp_chat
streamlit run main.py

# MCP integration application
cd src/streamlit-mcp-server-src/mcp_integration
streamlit run app_integrated_main.py
```

### 3. 🔌 FastAPI Multi-Agent Extensible API (`uv-agent-api/`)

**LangGraph StateGraph-based Agent System** - Extensible architecture

#### Features
- **StateGraph-based**: State management with LangGraph
- **RESTful API**: Standard HTTP endpoints
- **Programmatic Access**: Easy integration with existing applications
- **Conversation Management**: Built-in conversation history and state management
- **Scalable Architecture**: Client-server separation for better performance

#### Usage Example
```bash
# Start server
cd src/uv-agent-api
uvicorn uv_api_main:app --reload --port 8001

# Use client
python uv_api_client.py
```

### 4. 🤖 Multi-Agent Supervisor (`langgraph-supervisor/`) 🆕

**Advanced Multi-Agent System** with 7 specialized agents working in coordination

#### Features
- **🤖 Multi-Agent**: 7 specialized agents working in coordination
- **🎯 Specialized Domains**: Each agent specializes in specific tasks
- **🔄 Automatic Routing**: Supervisor automatically selects optimal agents
- **💻 Multiple Interfaces**: CLI, GUI, MCP tool integration
- **🤖 Multi-Model Support**: OpenAI GPT-4o, Anthropic Claude-3 series support

#### Agent Configuration

<div align="center">

#### 🎯 Supervisor Layer
**Task Router & Coordinator** - Request analysis, agent selection, result integration

#### 🤖 Agent Layer

| Agent | Specialization | Supported APIs | Main Functions |
|-------|---------------|----------------|----------------|
| 📅 **Scheduler Agent** | Schedule Management | Google Calendar API | Schedule addition, management, relative date processing |
| 🎵 **Music Agent** | Music Search & Recommendations | Spotify API | Track, artist, playlist search |
| 🍽️ **Restaurant Agent** | Restaurant Search | HotPepper + Google Maps | Integrated search, ratings, map display |
| 🎬 **Video Agent** | Video Search | YouTube Data API | Video search, information retrieval, metadata |
| 🏨 **Travel Agent** | Travel Planning | Jalan.net + Airbnb | Hotel, accommodation search |
| 🔢 **Math Agent** | Mathematical Calculations | - | Advanced mathematical processing, calculations |
| 🔍 **Research Agent** | Information Gathering | Tavily Search | Web search, research, information organization |

</div>

#### Usage Example
```bash
# CLI interface
python src/langgraph-supervisor/cli/supervisor_workers_multiagents.py

# GUI interface
streamlit run src/langgraph-supervisor/gui/streamlit_app.py

# Script execution
python -c "
from src.langgraph-supervisor.cli.supervisor_workers_multiagents import app
result = app.invoke({'messages': [{'role': 'user', 'content': 'Schedule a meeting for tomorrow at 3 PM'}]})
print(result['messages'][-1]['content'])
"
```

## 🤖 Multi-Agent System

### Workflow Diagram

![Multi-Agent Workflow](src/langgraph-supervisor/assets/workflow.png)

### Supervisor Role

The supervisor provides the following functions:

<div align="center">

| 🎯 **Task Analysis** | 🤖 **Agent Selection** | 🔄 **Coordination Management** |
|---------------------|----------------------|-------------------------------|
| Analyze user requests | Automatically select optimal specialized agents | Manage coordinated operation of multiple agents |

| 📊 **Result Integration** | ⚡ **Performance Optimization** |
|---------------------------|--------------------------------|
| Integrate and organize results from each agent | Efficient task execution |

</div>

### Agent Coordination

```
User Request → Supervisor → Specialized Agent Selection → Task Execution → Result Integration → Response
```

## ⚙️ Setup

### 1. Environment Requirements

```bash
Python 3.8+
Streamlit 1.28+ (for GUI usage)
```

### 2. Install Dependencies

```bash
# Basic dependencies
pip install -r requirements.txt

# Multi-agent system dependencies
pip install -r src/langgraph-supervisor/requirements.txt

# GUI dependencies
pip install -r src/langgraph-supervisor/gui/requirements.txt
```

### 3. Environment Variables

Create a `.env` file and set the following API keys:

```env
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

# Google APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
GOOGLE_CALENDAR_ID=your_calendar_id

# HotPepper Gourmet API
RECRUIT_API_KEY=your_recruit_api_key

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Google Search API (for uv-agent-api)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here

# ===== Optional Settings =====
# Authentication (for Streamlit interface)
USE_LOGIN=true
USER_ID=your_username
USER_PASSWORD=your_password
```

### 4. How to Get API Keys

<div align="center">

| API | How to Get | Link |
|-----|------------|------|
| **OpenAI API** | Generate API key with OpenAI account | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **Anthropic API** | Generate API key with Anthropic account | [Anthropic Console](https://console.anthropic.com/) |
| **Tavily API** | Create free account with Tavily | [Tavily API](https://tavily.com/) |
| **Google Custom Search** | Enable Custom Search API in Google Cloud Console | [Google Custom Search](https://developers.google.com/custom-search/v1/overview) |
| **Google Maps API** | Enable Maps API in Google Cloud Console | [Google Maps Platform](https://developers.google.com/maps/documentation/javascript/get-api-key) |
| **Hotpepper API** | Create account with Recruit Web Service | [Hotpepper API](https://webservice.recruit.co.jp/doc/hotpepper/) |
| **Spotify API** | Create app with Spotify Developer | [Spotify Developer](https://developer.spotify.com/documentation/web-api) |

</div>

## 🎮 Usage

### 🖥️ CLI Interface (Multi-Agent)

```bash
# Start multi-agent system
python src/langgraph-supervisor/cli/supervisor_workers_multiagents.py

# Script execution
python -c "
from src.langgraph-supervisor.cli.supervisor_workers_multiagents import app
result = app.invoke({'messages': [{'role': 'user', 'content': 'Schedule a meeting for tomorrow at 3 PM'}]})
print(result['messages'][-1]['content'])
"
```

### 🌐 GUI Interface (Multi-Agent)

```bash
# Start Streamlit application
streamlit run src/langgraph-supervisor/gui/streamlit_app.py

# Start English version application
streamlit run src/langgraph-supervisor/gui/streamlit_app_en.py

# Specify port
streamlit run src/langgraph-supervisor/gui/streamlit_app.py --server.port 8501

# Allow external access
streamlit run src/langgraph-supervisor/gui/streamlit_app.py --server.address 0.0.0.0
```

### 🎯 Simple ReAct Agent

```bash
# Start MCP servers
python src/simple-agent-mcp/tools/mcp_server_spotify.py
python src/simple-agent-mcp/tools/mcp_server_search.py
python src/simple-agent-mcp/tools/mcp_server_time.py

# Launch agent
python src/simple-agent-mcp/planner_agent.py
```

### 🌐 Streamlit Interface

```bash
# MCP chat application
cd src/streamlit-mcp-server-src/mcp_chat
streamlit run main.py

# MCP integration application
cd src/streamlit-mcp-server-src/mcp_integration
streamlit run app_integrated_main.py
```

### 🔌 FastAPI Multi-Agent API

```bash
# Start server
cd src/uv-agent-api
uvicorn uv_api_main:app --reload --port 8001

# Use client
python uv_api_client.py
```

## 🔌 API Integration

### Available Tools

#### 🗺️ Google Maps API
- Route search and directions
- Place search with ratings and business hours
- Geocoding (address to coordinates)
- Reverse geocoding (coordinates to address)

#### 🔍 Web Search
- Advanced web search with Tavily API
- Configurable search depth
- Rich search results with URLs

#### 🎵 Spotify Search
- Music search and recommendations
- Artist and album information
- Track details and audio features

#### ⏰ Time Service
- Current time for any timezone
- Timezone conversion
- Formatted time output

#### 📚 RAG (Retrieval-Augmented Generation)
- Document-based question answering
- PDF document processing
- Context-aware responses

### Multi-Agent API Integration Example

```python
# Basic usage
from src.langgraph-supervisor.cli.supervisor_workers_multiagents import app

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

## 🔄 Component Comparison

<div align="center">

| Feature | Simple ReAct Agent | Streamlit Interface | FastAPI Multi-Agent API | Multi-Agent Supervisor |
|---------|-------------------|-------------------|------------------------|----------------------|
| **User Interface** | Command line | Web UI | REST API | CLI, GUI, MCP |
| **Complexity** | Low (single ReAct) | Medium (ReAct) | High (StateGraph) | Highest (Multi-Agent) |
| **Use Case** | Basic functionality | Interactive use | Integration & Extension | Complex task processing |
| **Setup** | Multiple servers | Single app | Client-server | Integrated system |
| **Scalability** | Low | Medium | High | Highest |
| **Learning Curve** | Gentle | Gentle | Steep | Medium |
| **Multi-Agent Support** | No | No | Extensible | Full support |

</div>

## 🧩 Agent Workflow Examples

### Multi-Agent System Example

```txt
User: "Plan my weekend, find an Italian restaurant in Shibuya, and tell me about Beatles songs"
→ Supervisor: Analyze and split tasks
→ Scheduler Agent: Manage weekend schedule
→ Restaurant Agent: Search for Italian restaurants in Shibuya
→ Music Agent: Search for Beatles songs
→ Supervisor: Integrate and organize results
→ User: Receive integrated results
```

### Simple ReAct Agent Example

```txt
User: "Find a place to go this weekend"
→ Orchestrator: Route to "PlannerAgent"
→ PlannerAgent: Use web search MCP
→ Get info from Google Maps MCP + HotPepper MCP
→ Return results to user via LangGraph
```

## 🔮 Future Plans

- 🧠 Integration with LangChain memory
- 🔍 RAG (Retrieval-Augmented Generation) for dynamic search
- 📆 Google Calendar integration for automatic scheduling
- 📎 Notion auto-summary feature
- 🎤 Integration with YouTube audio separation tools
- 💬 Prompt optimization for each agent
- 🗺️ Visual workflow generation with LangGraph SDK

## ✨ Use Cases

<div align="center">

| Use Case | Description | Supported Components |
|----------|-------------|---------------------|
| 🎵 Music Search | Search and recommend songs from Spotify based on user requests | All components |
| 🍺 Party Venue Finder | Find good venues and check availability based on number, date, and area | Multi-Agent |
| 🌤 Weather Info | Get weather information for current or specified locations and provide advice | All components |
| 📆 Task Manager | Manage schedules and ToDo lists via Google Calendar integration | Multi-Agent |
| 📍 Outing Ideas | Suggest popular weekend spots and get reviews | All components |
| 🗺️ Route Planning | Get detailed directions and route information using Google Maps API | All components |
| 🔍 Web Research | Perform comprehensive web searches for information gathering | All components |

</div>

## 🔧 Troubleshooting

### Common Issues

#### 1. API Authentication Error

```bash
# Error: API credentials not configured
# Solution: Set API keys correctly in .env file
echo "OPENAI_API_KEY=your_key" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env
```

#### 2. Dependency Error

```bash
# Error: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt
pip install -r src/langgraph-supervisor/requirements.txt
```

#### 3. Port Conflict Error

```bash
# Error: Port already in use
# Solution: Use different port
streamlit run app.py --server.port 8502
uvicorn main:app --port 8002
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get detailed error information
try:
    result = app.invoke({"messages": [{"role": "user", "content": "test"}]})
except Exception as e:
    print(f"Error details: {e}")
    import traceback
    traceback.print_exc()
```

## 👤 Author

**Centaurus-Ken（[@ken-hori-2](https://github.com/ken-hori-2)）**

A developer experimenting with Agentic AI systems using LangGraph × MCP.  
From ideation to demo development and presentation, focusing on real-world use cases like music, weather, party planning, and schedule management.  
Also experienced in edge AI model design, demo development, and CI/CD pipeline automation.

## 📄 License

MIT License.

Created by Centaurus-Ken for exploring next-gen LLM applications with modular tool orchestration.

---

<div align="center">

**⭐️ If this project was helpful, please give it a star!**

</div> 