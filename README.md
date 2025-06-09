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