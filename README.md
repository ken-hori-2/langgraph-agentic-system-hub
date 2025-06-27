# LangGraph Agentic System Hub

🧠 A modular and extensible framework for building multi-agent LLM applications using LangGraph and MCP tools.

---

## 🔥 Overview

This project provides a **LangGraph-based agentic architecture** that integrates various tools (e.g. weather, Spotify, Google Maps, etc.) via **MCP (Modular Command Protocol)** to enable intelligent and dynamic task execution.

The repository contains **three main components**:

1. **🎯 Simple ReAct Agent** (`simple-agent-mcp/`)
   - Single ReAct agent that integrates MCP tools
   - Basic functionality like Spotify, web search, time retrieval
   - Command-line interface

2. **🌐 Streamlit MCP Server Interface** (`streamlit-mcp-server-src/`)
   - User-friendly web interface with ReAct agent
   - Dynamic MCP tool management
   - Real-time streaming responses

3. **🔌 FastAPI Multi-Agent Extensible API** (`uv-agent-api/`)
   - LangGraph StateGraph-based agent system
   - Extensible architecture for multi-agent systems with RESTful API access

It is designed to support:
- 🗺️ Weekend spot planning with web search & map tools
- 🍻 Party venue search with availability checks (HotPepper, Tabelog)
- 🎧 Spotify music search & playback based on requests
- ✅ Task management using calendar & to-do tools
- 🎯 A unified orchestrator to route tasks to the best agent

---

## 🏗️ Project Structure

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

## 🔧 Requirements

```txt
# LangChain Related
langchain==0.3.13
langchain-community==0.3.13
langchain-core==0.3.40
langchain-google-community==2.0.3
langchain-google-genai==2.0.11
langchain-openai==0.2.6
langchain-text-splitters==0.3.4
langgraph==0.2.45

# LLM Related
openai==1.54.3
anthropic==0.52.1
google-ai-generativelanguage==0.6.16

# Data Processing & Analysis
pandas==2.2.3
numpy==1.26.4
scikit-learn==1.6.1
scipy==1.15.2

# Web Related
fastapi==0.115.11
uvicorn==0.34.0
streamlit==1.45.1
flask==3.1.0
flask-cors==5.0.1

# Utilities
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.7.0
tqdm==4.67.0
```

You can install all dependencies at once with:
```bash
pip install -r requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone & install dependencies

```bash
git clone https://github.com/kenji/langgraph-agentic-system-hub.git
cd langgraph-agentic-system-hub
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory with the following variables:

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

#### How to Get API Keys

1. **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Anthropic API Key**: [Anthropic Console](https://console.anthropic.com/)
3. **Tavily API Key**: [Tavily](https://tavily.com/)
4. **Spotify API**: [Spotify Developer Dashboard](https://developer.spotify.com/)
5. **Google Maps API**: [Google Cloud Console](https://console.cloud.google.com/)
6. **Google Search API**: [Google Custom Search](https://developers.google.com/custom-search)

### 3. Available Tools

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

### 4. Choose Your Component

This repository provides three independent implementations:

---

## 🎯 Component 1: Simple ReAct Agent

### Overview

The **Simple ReAct Agent** is a single ReAct agent that integrates MCP tools. It uses LangGraph's `create_react_agent` to provide basic functionality like Spotify, web search, and time retrieval.

### Quick Start

#### 1. Run MCP Tool Servers

Start the required MCP servers:

```bash
# Terminal 1: Spotify MCP Server
python src/simple-agent-mcp/tools/mcp_server_spotify.py

# Terminal 2: Search MCP Server
python src/simple-agent-mcp/tools/mcp_server_search.py

# Terminal 3: Time MCP Server
python src/simple-agent-mcp/tools/mcp_server_time.py
```

#### 2. Launch the Agent

```bash
python src/simple-agent-mcp/planner_agent.py
```

### Features

- **MCP Tool Integration**: Integration with multiple MCP servers
- **ReAct Reasoning**: Combination of tool usage and reasoning
- **Simple Interaction**: Direct conversation via command line
- **Basic Features**: Music search, web search, time retrieval

### Use Cases

- Understanding MCP tool integration basics
- Building simple AI assistants
- CLI-based automation
- Prototype development

---

## 🌐 Component 2: Streamlit MCP Server Interface

### Overview

The **Streamlit MCP Server Interface** provides a user-friendly web-based interface for interacting with MCP tools through a ReAct agent. It's perfect for users who prefer a graphical interface and want to easily manage multiple tools.

### Quick Start

```bash
cd src/streamlit-mcp-server-src
streamlit run app_onlygpt_ken.py
```

### Features

- 🎯 **ReAct Agent**: Intelligent agent that can use multiple tools to answer questions
- 🔧 **Dynamic Tool Management**: Add and configure MCP tools through the web interface
- 🗺️ **Google Maps Integration**: Route search, place search, geocoding, and reverse geocoding
- 🔍 **Web Search**: Powered by Tavily search API
- 🎵 **Spotify Integration**: Music search and recommendations
- ⏰ **Time Services**: Current time for different timezones
- 📚 **RAG Support**: Document-based question answering
- 🔐 **Optional Authentication**: Login system for secure access
- 💬 **Real-time Streaming**: Live response streaming with tool call information

### Advanced Features

#### Authentication System

Enable login protection by setting `USE_LOGIN=true` in `.env`:

```bash
USE_LOGIN=true
USER_ID=your_username
USER_PASSWORD=your_password
```

#### Model Selection

Choose from multiple LLM models:
- **Anthropic**: Claude 3.7 Sonnet, Claude 3.5 Sonnet, Claude 3.5 Haiku
- **OpenAI**: GPT-4o, GPT-4o Mini

#### Response Settings

- **Timeout**: Adjust response generation time limit (60-300 seconds)
- **Recursion Limit**: Control tool call recursion depth (10-200)
- **Conversation Memory**: Automatic conversation history management

### Use Cases

- Interactive web-based AI assistance
- Tool exploration and experimentation
- User-friendly AI interface for non-technical users
- Real-time AI interactions with visual feedback

---

## 🔌 Component 3: FastAPI Multi-Agent Extensible API

### Overview

The **FastAPI Multi-Agent Extensible API** is a LangGraph StateGraph-based agent system. While currently implemented as a single agent, it has an extensible architecture that can be expanded to multi-agent systems in the future.

### Quick Start

#### 1. Start the Server

```bash
cd src/uv-agent-api
uvicorn uv_api_main:app --reload --port 8001
```

#### 2. Use the Client

In another terminal:

```bash
cd src/uv-agent-api
python uv_api_client.py
```

### API Endpoints

- `POST /ask` : Send a question and get the AI agent's response
- `GET /history` : Retrieve conversation history
- `DELETE /history` : Clear conversation history

### Integration Example

```python
import requests

# Send a question to the agent
response = requests.post("http://localhost:8001/ask", 
                        json={"question": "What's the weather like in Tokyo?"})
result = response.json()
print(result["response"])

# Get conversation history
history = requests.get("http://localhost:8001/history")
print(history.json())
```

### Features

- **StateGraph-based**: State management with LangGraph
- **RESTful API**: Standard HTTP endpoints
- **Programmatic Access**: Easy integration with existing applications
- **Conversation Management**: Built-in conversation history and state management
- **Scalable Architecture**: Client-server separation for better performance

### Multi-Agent Extensibility

While currently implemented as a single agent, it can be extended to multi-agent systems for the following reasons:

- **StateGraph Architecture**: Ability to add multiple nodes and edges
- **State Management**: Flexible state management with `AgentState`
- **Modular Design**: Easy addition of new agent nodes

### Use Cases

- Integration with existing web applications
- Mobile app backends
- Automated workflows and scripts
- Custom AI interfaces
- Microservices architecture
- Foundation for multi-agent systems

---

## 🔄 Component Comparison

| Feature | Simple ReAct Agent | Streamlit Interface | FastAPI Multi-Agent API |
|---------|-------------------|-------------------|------------------------|
| **User Interface** | Command line | Web UI | REST API |
| **Complexity** | Low (single ReAct) | Medium (ReAct) | High (StateGraph) |
| **Use Case** | Basic functionality | Interactive use | Integration & Extension |
| **Setup** | Multiple servers | Single app | Client-server |
| **Scalability** | Low | Medium | High |
| **Learning Curve** | Gentle | Gentle | Steep |
| **Multi-Agent Support** | No | No | Extensible |

---

## 🧩 Agentic Workflow Example

```txt
User: "Find a place to go this weekend"
→ Orchestrator: routes to "PlannerAgent"
→ PlannerAgent: uses web search MCP
→ Gets info from Google Maps MCP + HotPepper MCP
→ Returns results to user via LangGraph
```

## 🔮 Future Plans

- 🧠 Memory integration with LangChain memory
- 🔍 RAG (Retrieval-Augmented Generation) for dynamic search
- 📆 Google Calendar integration for automatic scheduling
- 📎 Notion auto-summary feature
- 🎤 Integration with YouTube audio separation tools
- 💬 Prompt optimization for each agent
- 🗺️ Visual workflow generation with LangGraph SDK

## ✨ Example Use Cases

| Use Case         | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| 🎵 Music Search  | Search and recommend songs from Spotify based on user requests.              |
| 🍺 Party Finder  | Find good venues and check availability based on number, date, and area.     |
| 🌤 Weather Info  | Get weather information for current or specified locations and provide advice.|
| 📆 Task Manager  | Manage schedules and ToDo lists via Google Calendar integration.             |
| 📍 Outing Ideas  | Suggest popular weekend spots and get reviews.                               |
| 🗺️ Route Planning| Get detailed directions and route information using Google Maps API.         |
| 🔍 Web Research  | Perform comprehensive web searches for information gathering.                |

## 👤 Author

**Centaurus-Ken（[@ken-hori-2](https://github.com/ken-hori-2)）**

A developer experimenting with Agentic AI systems using LangGraph × MCP.  
From ideation to demo development and presentation, focusing on real-world use cases like music, weather, party planning, and schedule management.  
Also experienced in edge AI model design, demo development, and CI/CD pipeline automation.

## 📄 License

MIT License.

Created by Centaurus-Ken for exploring next-gen LLM applications with modular tool orchestration.

---