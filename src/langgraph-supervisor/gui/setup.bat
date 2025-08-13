@echo off
REM 🧠 Agentic AI Multi-Agent Assistant Setup Script for Windows
REM This script sets up the environment for the multi-agent web application

echo 🚀 Setting up Agentic AI Multi-Agent Assistant...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo ⚠️ .env file not found. Creating template...
    (
        echo # OpenAI API
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Anthropic API
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
        echo.
        echo # Tavily API
        echo TAVILY_API_KEY=your_tavily_api_key_here
        echo.
        echo # Google Custom Search
        echo GOOGLE_CSE_ID=your_google_cse_id_here
        echo.
        echo # Google Maps API
        echo GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
        echo.
        echo # Hotpepper API
        echo HOTPEPPER_API_KEY=your_hotpepper_api_key_here
        echo.
        echo # Spotify API
        echo SPOTIFY_USER_ID=your_spotify_user_id_here
        echo SPOTIFY_TOKEN=your_spotify_token_here
        echo.
        echo # Optional: LangSmith
        echo # LANGSMITH_API_KEY=your_langsmith_api_key_here
        echo # LANGSMITH_TRACING=true
        echo # LANGSMITH_ENDPOINT=https://api.smith.langchain.com
        echo # LANGSMITH_PROJECT=LangGraph-MCP-Agents
        echo.
        echo # Login settings
        echo USE_LOGIN=false
        echo USER_ID=admin
        echo USER_PASSWORD=admin1234
    ) > .env
    echo 📝 Please edit .env file with your actual API keys
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Run Japanese version: streamlit run streamlit_app.py
echo 4. Run English version: streamlit run streamlit_app_en.py
echo.
echo 🌐 Access the application at: http://localhost:8501
echo.
echo 📖 For more information, see README.md
pause 