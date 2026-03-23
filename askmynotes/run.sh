#!/bin/bash
# Simple launcher script for Ask My Notes app

cd /Users/anubhav/agentic-ai/askmynotes
source .venv/bin/activate

echo "🚀 Starting Ask My Notes..."
echo "📚 Streamlit app will open at: http://localhost:8501"
echo ""

streamlit run app.py --logger.level=error
