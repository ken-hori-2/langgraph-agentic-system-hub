# LangGraph Agentic System Hub

🧠 A modular and extensible framework for building multi-agent LLM applications using LangGraph and MCP tools.

---

## 🔥 Overview

This project provides a **LangGraph-based agentic architecture** that integrates various tools (e.g. weather, Spotify, Google Maps, etc.) via **MCP (Modular Command Protocol)** to enable intelligent and dynamic task execution.

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
├── README.md                  # Project documentation
├── requirements.txt           # Dependency list
├── main.py                    # Application entry point
│
├── agents/                    # LangGraph node logic for each agent
│   ├── orchestrator.py        # Central agent for task routing
│   ├── music_agent.py         # Agent for music-related tasks (Spotify, etc.)
│   ├── event_agent.py         # Agent for party/outing suggestions
│   └── weather_agent.py       # Agent for weather information
│
├── tools/                     # MCP servers for external tools (FastMCP)
│   ├── spotify_mcp.py         # MCP server for Spotify search
│   ├── weather_mcp.py         # MCP server for weather info
│   ├── map_search_mcp.py      # Google Maps / HotPepper / Tabelog integration
│   └── calendar_mcp.py        # Google Calendar / TODO management (planned)
│
├── graphs/                    # LangGraph workflow definitions
│   └── planner_graph.py       # Multi-agent workflow definition
│
├── memory/                    # LangChain Memory (conversation history)
│   └── memory_config.py       # Memory save/restore logic (e.g. ChatMessageHistory)
│
├── ui/                        # User interface (e.g. Gradio)
│   └── web_ui.py              # Web-based chat UI (in development)
│
├── tests/                     # Tests for tools and agents
│   └── test_spotify_mcp.py    # Spotify MCP test
│
├── src/streamlit-mcp-server-src/  # Streamlit-based MCP server interface
│   ├── app_onlygpt_ken.py     # Main Streamlit application
│   ├── mcp_server_time.py     # Time service MCP server
│   ├── mcp_server_search.py   # Web search MCP server
│   ├── mcp_server_spotify.py  # Spotify search MCP server
│   ├── mcp_server_googlemaps.py # Google Maps API MCP server
│   ├── mcp_server_rag.py      # RAG (Retrieval-Augmented Generation) MCP server
│   ├── config.json            # MCP server configuration
│   └── utils.py               # Utility functions
│
└── docs/                      # Architecture docs and use cases
    └── architecture.png       # Diagrams, flowcharts, etc.
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

## 🚀 Getting Started

### 1. Clone & install dependencies

```bash
git clone https://github.com/kenji/langgraph-agentic-system-hub.git
cd langgraph-agentic-system-hub
pip install -r requirements.txt
```

### 2. Run a tool MCP server
```bash
python src/tools/mcp_server_spotify.py
# or
python src/tools/mcp_server_time.py
# or
python src/tools/mcp_server_search.py
```

### 3. Run the LangGraph agent
```bash
python src/planner_agent.py
```

### 4. Launch the Gradio UI (coming soon)
```bash
python ui/web_ui.py
```

---

## 🌐 Streamlit MCP Server Interface

### Overview

The **Streamlit MCP Server Interface** provides a user-friendly web-based interface for interacting with MCP tools through a ReAct agent. It allows users to easily add, configure, and use various MCP tools including Google Maps API, web search, Spotify, and more.

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

### Quick Start

#### 1. Environment Setup

Create a `.env` file in the `src/streamlit-mcp-server-src/` directory:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Tool API Keys
TAVILY_API_KEY=your_tavily_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Optional: Authentication
USE_LOGIN=true
USER_ID=your_username
USER_PASSWORD=your_password
```

#### 2. Launch the Application

```bash
cd src/streamlit-mcp-server-src
streamlit run app_onlygpt_ken.py
```

#### 3. Configure Tools

1. Open the web interface in your browser
2. Go to the sidebar and click "Apply Settings" to initialize the default tools
3. Use "Add MCP Tools" to add additional tools as needed

### Available Tools

#### 🗺️ Google Maps API (`mcp_server_googlemaps.py`)

**Features:**
- Route search and directions
- Place search with ratings and business hours
- Geocoding (address to coordinates)
- Reverse geocoding (coordinates to address)

**Setup:**
1. Get Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable required APIs:
   - Maps JavaScript API
   - Directions API
   - Geocoding API
   - Places API
3. Add `GOOGLE_MAPS_API_KEY=your_key` to `.env`

**Usage Examples:**
- "東京駅から渋谷駅までのルートを教えて"
- "渋谷駅周辺のレストランを探して"
- "東京都渋谷区の座標を教えて"

#### 🔍 Web Search (`mcp_server_search.py`)

**Features:**
- Advanced web search with Tavily API
- Configurable search depth
- Rich search results with URLs

**Setup:**
1. Get Tavily API key from [Tavily](https://tavily.com/)
2. Add `TAVILY_API_KEY=your_key` to `.env`

#### 🎵 Spotify Search (`mcp_server_spotify.py`)

**Features:**
- Music search and recommendations
- Artist and album information
- Track details and audio features

**Setup:**
1. Create Spotify app in [Spotify Developer Dashboard](https://developer.spotify.com/)
2. Add credentials to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

#### ⏰ Time Service (`mcp_server_time.py`)

**Features:**
- Current time for any timezone
- Timezone conversion
- Formatted time output

#### 📚 RAG (Retrieval-Augmented Generation) (`mcp_server_rag.py`)

**Features:**
- Document-based question answering
- PDF document processing
- Context-aware responses

**Setup:**
1. Place documents in the `data/` directory
2. The system will automatically process and index them

### Configuration

#### Adding Custom Tools

1. Create a new MCP server file (e.g., `mcp_server_custom.py`)
2. Follow the FastMCP pattern from existing servers
3. Add the tool configuration to `config.json`:

```json
{
  "custom_tool": {
    "command": "python",
    "args": ["./mcp_server_custom.py"],
    "transport": "stdio"
  }
}
```

#### Tool Configuration Format

```json
{
  "tool_name": {
    "command": "python",
    "args": ["./mcp_server_toolname.py"],
    "transport": "stdio"
  }
}
```

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

### Troubleshooting

#### Common Issues

1. **API Key Errors**
   - Ensure all required API keys are set in `.env`
   - Check API key validity and quotas

2. **Tool Connection Issues**
   - Verify MCP server files are executable
   - Check `config.json` syntax
   - Ensure all dependencies are installed

3. **Streamlit Issues**
   - Clear browser cache
   - Restart Streamlit server
   - Check port availability

#### Debug Mode

Enable debug information by setting environment variables:

```bash
STREAMLIT_LOG_LEVEL=debug
```

### Development

#### Adding New MCP Tools

1. **Create MCP Server**:
   ```python
   from mcp.server.fastmcp import FastMCP
   
   mcp = FastMCP("YourToolName")
   
   @mcp.tool()
   async def your_tool_function(param: str) -> str:
       # Your tool logic here
       return "Result"
   
   if __name__ == "__main__":
       mcp.run(transport="stdio")
   ```

2. **Update Configuration**:
   - Add tool to `config.json`
   - Update default settings in `app_onlygpt_ken.py`

3. **Test Integration**:
   - Restart Streamlit application
   - Test tool functionality through the interface

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

## Appendix: FastAPI + Uvicorn MCP Agent API Example

This repository also includes a sample implementation of an MCP agent API using FastAPI and Uvicorn.

### Directory Structure

```
src/uv_agent_api/
  ├── uv_api_agent.py   # Agent core (LangGraph/LLM/Tool definitions)
  ├── uv_api_main.py    # FastAPI server launcher
  └── uv_api_client.py  # API client (for sending requests)
```

### 1. Start the Server

```bash
cd src/uv_agent_api
uvicorn uv_api_main:app --reload --port 8001
```

### 2. Example: Using the Client

In another terminal:

```bash
cd src/uv_agent_api
python uv_api_client.py
```

- You can interact with the AI agent in a chat format.
- Type `quit` or `exit` to end the session.

### 3. API Endpoints

- `POST /ask` : Send a question and get the AI agent's response
- `GET /history` : Retrieve conversation history
- `DELETE /history` : Clear conversation history

### 4. Notes
- `uv_api_agent.py` … Defines LangGraph/LLM/Tools/conversation memory and the agent core
- `uv_api_main.py` … FastAPI server endpoint definitions
- `uv_api_client.py` … Client for sending requests to the server

If you need to use API keys or connect to external services, please refer to the comments and environment variable settings in each script. 