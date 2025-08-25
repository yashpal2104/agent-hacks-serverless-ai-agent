#!/bin/bash
"""
🚀 Celebrity AI Assistant Suite - Streamlit Launcher
==================================================
Launch the beautiful web frontend for all celebrity AI features
"""

echo "🎭🚀 Starting Celebrity AI Assistant Suite Web Interface..."
echo "========================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "agent-venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv agent-venv && source agent-venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source agent-venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing Streamlit dependencies..."
    pip install streamlit==1.28.1 streamlit-webrtc==0.47.1 pyttsx3==2.90 pygame==2.5.2
fi

# Create frames directory if it doesn't exist
mkdir -p frames

# Check environment variables
echo "🔍 Checking configuration..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️ Warning: GOOGLE_API_KEY not set"
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "⚠️ Warning: GOOGLE_APPLICATION_CREDENTIALS not set"
fi

if [ -z "$PORTIA_API_KEY" ]; then
    echo "⚠️ Warning: PORTIA_API_KEY not set"
fi

echo ""
echo "🌟 Launching Celebrity AI Assistant Suite Web Interface..."
echo "📱 The app will open in your default browser"
echo "🔗 URL: http://localhost:8501"
echo ""
echo "Available features:"
echo "  🎥 Live David Attenborough Webcam Narrator"
echo "  📅 Celebrity Calendar Assistant with Real Google Calendar"
echo "  💬 Multi-Celebrity Companion Chat with Voice"
echo "  ⚙️ Settings and System Configuration"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================"

# Launch Streamlit app
streamlit run streamlit_app.py --server.port=8501 --server.headless=false
