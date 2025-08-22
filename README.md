# Celebrity Companion AI - Portia SDK Multi-Agent Edition

A sophisticated AI companion system featuring celebrity personalities with Google Cloud Text-to-Speech integration, powered by Portia SDK's three-agent architecture.

## 🎭 Features

- **4 Celebrity Personalities**: David Attenborough, Morgan Freeman, Scarlett Johansson, Peter Griffin
- **Intelligent Celebrity Selection**: Automatically selects the best celebrity based on your message analysis
- **Portia SDK Integration**: Multi-agent orchestration with Planning, Execution, and Introspection agents
- **Google Gemini AI**: Powers intelligent celebrity responses
- **Google Cloud TTS**: High-quality voice synthesis with customized voice characteristics
- **Interactive Chat**: Switch between celebrities and have natural conversations
- **Audio Playback**: Supports both PulseAudio and ALSA

## 🎵 Voice Characteristics

Each celebrity has unique voice characteristics that are incorporated into their responses:

- **Scarlett Johansson**: Smooth, slightly husky, modern voice with gentle pace and warm curiosity
- **Morgan Freeman**: Deep, steady, resonant tone with dramatic pauses and profound wisdom
- **David Attenborough**: Gentle, breathy, awe-inspired British accent with slow, deliberate pacing
- **Peter Griffin**: Playful, exaggerated, nasal quality with spontaneous laughter and goofy asides

## 🚀 Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up Google Cloud**: Follow [GOOGLE_TTS_SETUP.md](GOOGLE_TTS_SETUP.md)
3. **Configure environment**: Set up your `.env` file with API keys
4. **Run the app**: `python3 celebrity_companion_ai_clean.py`

## 📁 Project Structure

- `celebrity_companion_ai_clean.py` - Main application with Portia SDK integration
- `demo_google_tts.py` - Setup verification and usage demo
- `GOOGLE_TTS_SETUP.md` - Comprehensive setup guide
- `requirements.txt` - Python dependencies
- `companion_audio/` - Generated audio files
- `celebrity_audio/` - Sample celebrity audio files

## 🎯 Usage

- Type normally to chat with celebrities
- Use `switch to [celebrity]` to change voices
- Type `voices` to see all voice characteristics
- Type `info` for current celebrity details
- Type `quit` to exit
- Available celebrities: `scarlett`, `morgan`, `david`, `peter`

## 🧠 Portia SDK Architecture

The system uses Portia's three-agent architecture:

1. **Planning Agent**: Analyzes conversation context and plans response strategies
2. **Execution Agent**: Generates celebrity responses and handles TTS operations
3. **Introspection Agent**: Monitors conversation state and adapts strategies

## 🔧 Requirements

- Python 3.8+
- Google Gemini API key
- Google Cloud TTS service account
- Audio system (PulseAudio or ALSA)
- Portia SDK (optional, falls back to simple mode if unavailable)

## 📖 Documentation

- [Setup Guide](GOOGLE_TTS_SETUP.md) - Complete setup instructions
- [Demo Script](demo_google_tts.py) - Test your setup

## 🎵 Audio Support

The system automatically detects available audio systems and will work in text-only mode if TTS isn't configured. For full voice experience, follow the Google Cloud TTS setup guide.

## 🎭 Voice Switching

The system intelligently suggests celebrity switches based on:
- User's emotional state
- Conversation topic
- Response intensity
- Previous interaction patterns

Each celebrity brings their unique voice, personality, and expertise to provide the most appropriate support for your conversation.

## 🧠 Intelligent Celebrity Selection

The system automatically analyzes your message and selects the most appropriate celebrity:

- **David Attenborough**: Anxiety, overwhelm, stress → Nature wisdom and calming presence
- **Morgan Freeman**: Sadness, grief, loneliness, confusion → Deep comfort and existential wisdom  
- **Scarlett Johansson**: Anger, frustration, relationships → Modern psychology and emotional validation
- **Peter Griffin**: Work issues, light topics → Relatable peer support and humor

No need to manually select - just start typing and the system will choose the perfect companion for your needs!