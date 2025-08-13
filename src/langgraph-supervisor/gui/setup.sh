#!/bin/bash

# 🧠 Agentic AI Multi-Agent Assistant Setup Script
# This script sets up the environment for the multi-agent web application

echo "🚀 Setting up Agentic AI Multi-Agent Assistant..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version+ is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating template..."
    cat > .env << EOF
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
EOF
    echo "📝 Please edit .env file with your actual API keys"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run Japanese version: streamlit run streamlit_app.py"
echo "4. Run English version: streamlit run streamlit_app_en.py"
echo ""
echo "🌐 Access the application at: http://localhost:8501"
echo ""
echo "📖 For more information, see README.md" 