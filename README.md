# 🎬🤖 AI Agent Hacks - Serverless Celebrity AI Assistant Suite

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Portia SDK](https://img.shields.io/badge/Portia%20SDK-v0.7.0-green.svg)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-TTS%20%26%20Gemini-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**The Ultimate Celebrity AI Assistant Suite with Real-World Integration**

*Transform your digital life with AI-powered celebrity companions that manage your emails, calendar, and provide live commentary with authentic voices!*

</div>

---

## 🌟 **What Makes This Special?**

This isn't just another chatbot - it's a **complete AI ecosystem** that brings celebrities to life in your digital world. From managing your Google Calendar with David Attenborough's wisdom to having Morgan Freeman read your emails, this suite creates truly magical experiences.

---

## 🎭 **Featured Celebrity Personalities**

### **🌿 Sir David Attenborough** - *Nature Documentary Narrator*
- **Specialty**: Webcam commentary, Calendar management, Anxiety relief
- **Voice**: Premium British `en-GB-Journey-D` with documentary pacing
- **Signature**: *"Here we observe a specimen of Homo sapiens in its natural habitat..."*

### **🎬 Morgan Freeman** - *The Voice of Wisdom*  
- **Specialty**: Email reading, Profound insights, Life guidance
- **Voice**: Deep, resonant tones with dramatic pauses
- **Signature**: *"Now, let me tell you about the nature of your inbox..."*

### **🔥 Scarlett Johansson** - *Modern Sophistication*
- **Specialty**: Relationship advice, Modern psychology, Emotional support
- **Voice**: Smooth, slightly husky with warm curiosity
- **Signature**: *"Darling, let's talk about what's really going on here..."*

### **😂 Peter Griffin** - *Comedy Relief Companion*
- **Specialty**: Work stress relief, Light conversations, Comic perspective
- **Voice**: Playful, exaggerated with spontaneous laughter
- **Signature**: *"Holy crap! Your calendar is more packed than a Family Guy episode!"*

---

## 🚀 **Core Applications**

### **📅 Celebrity Calendar Assistant** 
```bash
python celebrity_calendar_assistant.py
```
- **Real Google Calendar Integration** with live data reading
- **Celebrity Voice Announcements** for all events
- **Smart Event Management** (create, read, delete with confirmations)
- **Conversation History** - builds ongoing narrative context
- **Portia SDK Integration** for advanced task orchestration

**Features:**
- ✅ Reads your actual calendar events with celebrity flair
- ✅ Creates events with natural language processing
- ✅ Deletes events with smart confirmation system
- ✅ Premium Google Cloud TTS with journey voices
- ✅ Persistent conversation memory across sessions

### **🎥 David Attenborough Webcam Narrator**
```bash
python narrator.py
```
- **Live Webcam Analysis** with Google Gemini Vision AI
- **Continuous Documentary Commentary** with contextual awareness  
- **Conversation History Storage** in JSON format
- **Lazy Portia SDK Integration** for advanced insights
- **Auto-save Functionality** every 10 frames

**Features:**
- ✅ Real-time nature documentary narration of your webcam
- ✅ Context-aware commentary that builds ongoing stories
- ✅ Conversation persistence across sessions
- ✅ Smart frame analysis with Google Gemini AI
- ✅ Premium British voice with documentary timing

### **📧 Celebrity Email Reader** (Multiple Variants)
```bash
python celebrity_gmail_reader.py  # Or other email variants
```
- **Gmail Integration** with MCP (Model Context Protocol)
- **Celebrity Voice Reading** of your actual emails
- **Smart Email Summarization** with AI insights
- **Multi-personality Support** for different email types

---

## 🏗️ **Advanced Technology Stack**

### **🧠 AI & Language Models**
- **Google Gemini 1.5 Flash** - Vision and text analysis
- **Anthropic Claude 3.5 Haiku** - Conversational intelligence
- **OpenAI GPT-4** - Backup language processing

### **🎙️ Audio & TTS Systems**
- **Google Cloud Text-to-Speech** - Premium neural voices
- **Journey Voice Collection** - Ultra-natural British voices
- **Pyttsx3 Fallback** - Local TTS when cloud unavailable
- **Pygame Audio** - Seamless playback for all platforms

### **🔌 Integration Platforms**
- **Portia SDK** - Advanced multi-agent orchestration
- **Google Calendar API** - Real calendar data access
- **Gmail API with MCP** - Secure email reading
- **Google Cloud Vision** - Image analysis capabilities

### **💾 Data Management**
- **Conversation Persistence** - JSON-based session storage
- **Context Building** - Smart memory across interactions
- **Auto-save Systems** - Never lose conversation progress
- **Error Recovery** - Graceful handling of API failures

---

## 🎯 **Key Features & Capabilities**

### **🎭 Multi-Personality System**
- **Intelligent Celebrity Selection** based on context and mood
- **Voice Characteristic Matching** - each celebrity has unique speech patterns  
- **Contextual Personality Switching** for optimal user experience
- **Custom Voice Parameters** (rate, pitch, volume per celebrity)

### **🔊 Premium Audio Experience**
- **Google Cloud Neural Voices** with premium quality
- **Celebrity-Matched Voice Selection** for authentic experience
- **Multi-Platform Audio Support** (PulseAudio, ALSA, fallbacks)
- **Real-time Audio Generation** with caching for performance

### **🤖 Advanced AI Integration**
- **Multi-Model Support** - Gemini, Claude, GPT-4 compatibility
- **Context-Aware Responses** using conversation history
- **Task-Based Execution** with Portia's planning system  
- **Intelligent Error Handling** with graceful fallbacks

### **📊 Real-World Data Integration**
- **Live Google Calendar** - actual events, not mock data
- **Real Gmail Access** - secure email reading with MCP
- **Webcam Integration** - live video analysis and commentary
- **Persistent Sessions** - conversations continue across app restarts

---

## ⚙️ **Installation & Setup**

### **Prerequisites**
```bash
# Python 3.8+ required
python --version

# Virtual environment (recommended)
python -m venv agent-venv
source agent-venv/bin/activate  # Linux/Mac
# or
agent-venv\Scripts\activate     # Windows
```

### **Quick Install**
```bash
# Clone the repository
git clone https://github.com/yashpal2104/agent-hacks-serverless-ai-agent.git
cd agent-hacks-serverless-ai-agent

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### **API Keys Setup**
Edit your `.env` file with your API keys:

```env
# Google AI Services
GOOGLE_API_KEY=your_google_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=your_service_account.json

# Portia SDK
PORTIA_API_KEY=your_portia_api_key_here

# Optional: Anthropic (backup)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: ElevenLabs (premium voices)  
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### **Google Cloud Setup**
1. Create a Google Cloud Project
2. Enable Text-to-Speech API
3. Create a Service Account
4. Download JSON credentials
5. Set `GOOGLE_APPLICATION_CREDENTIALS` path

📚 **Detailed setup guide**: [GOOGLE_TTS_SETUP.md](GOOGLE_TTS_SETUP.md)

---

## 🎮 **Usage Examples**

### **Calendar Management with Celebrity Flair**
```python
# David Attenborough reading your schedule
"Here we observe the fascinating ritual of the 'daily standup meeting' - 
a curious gathering where humans congregate to discuss their territorial 
progress in the digital realm..."

# Morgan Freeman creating events  
"And so it was, on this Tuesday morning, that a new meeting was born into 
your calendar. A meeting that would change... everything."
```

### **Live Webcam Commentary**
```python  
# Frame 1: David analyzing your workspace
"Note the remarkable eyewear appendages - possibly designed to enhance 
visual acuity for this critical preening process."

# Frame 2: Building narrative continuity
"Here we observe the subject exhibiting a fascinating instance of 
'ocular-adjustment,' subtly shifting them to optimize its visual field."
```

### **Email Reading Experience**
```python
# Scarlett reading work emails
"Darling, it seems your boss has some... interesting priorities. 
This email about 'synergistic deliverables' is quite something."

# Peter Griffin on spam emails
"Holy crap! Someone thinks you've won the Nigerian lottery AGAIN! 
These scammers have less creativity than a Family Guy rerun!"
```

---

## 📁 **Project Structure**

```
📦 agent-hacks-serverless-ai-agent/
├── 🎭 **Core Applications**
│   ├── celebrity_calendar_assistant.py      # Main calendar app with real data
│   ├── narrator.py                         # David Attenborough webcam narrator  
│   ├── celebrity_gmail_reader.py          # Email reading with celebrities
│   └── celebrity_companion_ai_clean.py    # Multi-personality chatbot
│
├── 🔧 **Setup & Configuration**  
│   ├── .env.example                       # Environment variables template
│   ├── requirements.txt                   # Python dependencies
│   ├── GOOGLE_TTS_SETUP.md               # Detailed setup guide
│   └── demo_google_tts.py                # Setup verification script
│
├── 🎵 **Audio & Media**
│   ├── celebrity_audio/                  # Sample celebrity voices
│   ├── companion_audio/                  # Generated audio files
│   └── frames/                          # Webcam capture frames
│
├── 📊 **Data & Logs**  
│   ├── *.json                           # Conversation history files
│   ├── chat_history.json               # Persistent chat logs
│   └── .portia/                        # Portia SDK configuration
│
└── 🧪 **Development & Testing**
    ├── test_*.py                       # Test scripts
    ├── quick_test.py                   # Quick functionality tests
    └── various_demos.py                # Feature demonstrations
```

---

## 🎯 **Advanced Features**

### **🧠 Conversation Intelligence**
- **Persistent Memory**: Conversations continue across app restarts
- **Context Building**: AI builds upon previous interactions  
- **Smart Summarization**: Key points preserved across long sessions
- **Emotional Intelligence**: Celebrity selection based on user mood

### **⚡ Performance Optimizations**
- **Lazy Loading**: Portia SDK initializes only when needed
- **Audio Caching**: Generated speech cached for repeated phrases
- **Efficient Memory**: Conversation history automatically trimmed
- **Graceful Degradation**: Works even when some services are down

### **🔒 Security & Privacy**
- **Local Audio Processing**: Audio generated and played locally  
- **Secure API Integration**: Proper authentication for all services
- **Data Encryption**: Sensitive data handled securely
- **Privacy First**: No data stored on external servers unnecessarily

### **🎨 User Experience**
- **Beautiful CLI Interface**: Rich terminal output with emojis and formatting
- **Audio-Visual Feedback**: Clear indicators for all system states
- **Error Recovery**: Helpful error messages with suggested fixes
- **Cross-Platform**: Works on Linux, macOS, Windows

---

## 🎪 **Demo Scripts & Testing**

### **Quick Feature Test**
```bash
python quick_test.py          # Test basic functionality
python demo_google_tts.py     # Verify TTS setup  
python test_calendar_data.py  # Test calendar integration
```

### **Individual Component Tests**
```bash
# Test specific celebrity voices
python -c "from celebrity_calendar_assistant import *; test_voice('david')"

# Verify Google Cloud setup  
python -c "import google.cloud.texttospeech; print('✅ Google Cloud TTS ready!')"

# Check Portia SDK
python -c "from portia import Portia; print('✅ Portia SDK available!')"
```

---

## � **Upcoming Features**

### **🚀 Planned Enhancements**
- [ ] **Multi-Language Support** - Celebrity voices in different languages
- [ ] **Video Call Integration** - Real-time celebrity video appearances  
- [ ] **Smart Home Integration** - Control devices with celebrity commands
- [ ] **Meeting Transcription** - Live meeting notes with celebrity insights
- [ ] **Custom Voice Training** - Create your own celebrity voice clones

### **🧪 Experimental Features**
- [ ] **Emotion Detection** - Facial expression analysis for better responses
- [ ] **Voice Cloning** - Create custom celebrity personalities
- [ ] **AR Integration** - Augmented reality celebrity appearances
- [ ] **Multi-Agent Conversations** - Celebrities talking to each other

---

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

### **🎭 Add New Celebrities**
1. Create voice characteristics in `celebrity_voices.py`
2. Add personality prompts for the new celebrity  
3. Test with Google Cloud TTS voice matching
4. Submit PR with examples and documentation

### **🔧 Improve Features**
- Bug fixes and performance improvements
- New integration platforms (Slack, Discord, etc.)
- Enhanced conversation intelligence
- Better error handling and user experience

### **📚 Documentation**
- Setup guides for new platforms
- Video tutorials and demos  
- API documentation improvements
- Translation to other languages

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

### **🎭 Voice & AI Technologies**
- **Google Cloud** - Premium neural text-to-speech
- **Google Gemini** - Advanced vision and language AI
- **Anthropic Claude** - Conversational intelligence  
- **Portia SDK** - Multi-agent orchestration platform

### **🎪 Inspiration**  
- **Sir David Attenborough** - For decades of nature documentary excellence
- **Morgan Freeman** - For that unmistakable narrative voice
- **Scarlett Johansson** - For bringing AI characters to life in cinema
- **Seth MacFarlane** - For creating the irreverent Peter Griffin

### **🛠️ Open Source Community**
- All the amazing developers who built the foundational libraries
- Contributors who help improve the codebase
- Users who provide feedback and feature requests

---

## 📞 **Support & Community**

### **🐛 Issues & Bug Reports**
- [GitHub Issues](https://github.com/yashpal2104/agent-hacks-serverless-ai-agent/issues)
- Please include system info, error logs, and steps to reproduce

### **💬 Discussions & Feature Requests**  
- [GitHub Discussions](https://github.com/yashpal2104/agent-hacks-serverless-ai-agent/discussions)
- Share your celebrity AI experiences and ideas!

### **📧 Direct Contact**
- Project Maintainer: [@yashpal2104](https://github.com/yashpal2104)
- Email: [Add your email if desired]

---

<div align="center">

**🎭 "The future of AI isn't just artificial intelligence - it's artificial personality!" 🎭**

*Made with ❤️ by the AI Agent Hacks community*

⭐ **Star this repo if you enjoyed bringing celebrities to life with AI!** ⭐

</div>

---

## 🎯 **Quick Start Guide**

Ready to get started? Here's your 5-minute setup:

1. **Clone & Install**:
   ```bash
   git clone https://github.com/yashpal2104/agent-hacks-serverless-ai-agent.git
   cd agent-hacks-serverless-ai-agent
   pip install -r requirements.txt
   ```

2. **Setup API Keys**: 
   - Copy `.env.example` to `.env`
   - Add your Google API key and service account

3. **Test Your Setup**:
   ```bash
   python demo_google_tts.py
   ```

4. **Start Having Fun**:
   ```bash
   python celebrity_calendar_assistant.py  # For calendar magic
   python narrator.py                      # For webcam commentary  
   python celebrity_companion_ai_clean.py # For general chat
   ```

That's it! You now have AI celebrities managing your digital life! 🎉