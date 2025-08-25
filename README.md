# 🎬🤖 AI Agent Hacks — Serverless Celebrity AI Assistant Suite

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Portia SDK](https://img.shields.io/badge/Portia%20SDK-v0.7.0-green.svg)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-TTS%20%26%20Gemini-orange.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**The Ultimate Celebrity AI Assistant Suite — Real-World Integration, Flawless Experience**

*Transform your digital life with AI-powered celebrity companions that manage emails, calendars, and deliver live commentary in authentic voices!*

<img width="1920" height="1080" alt="Demo Screenshot" src="https://github.com/user-attachments/assets/9e6b5634-0073-4275-8b44-bbd5c8334f7e" />

---

## 🎥 Live Demo

Experience the magic in action!  
Watch the official demonstration of the Celebrity AI Assistant Suite:

[![Demo Video](https://img.youtube.com/vi/ggsxH0zwLXk/0.jpg)](https://youtu.be/ggsxH0zwLXk)

---

</div>

## 🌟 What Sets This Suite Apart

This isn’t just another chatbot — it’s an **immersive AI ecosystem**. Enjoy real-world celebrity personalities managing your Google Calendar, reading your emails, and narrating live webcam footage, all with authentic voices and personalities.

---

## 🎭 Featured Celebrity Personalities

- **🌿 Sir David Attenborough** — Nature documentary narration, gentle calendar management, anxiety relief  
  *Premium British documentary voice, contextual and soothing.*

- **🎬 Morgan Freeman** — Profound email readings, insightful life commentary  
  *Deep, resonant voice with dramatic flair.*

- **🔥 Scarlett Johansson** — Relationship advice, modern psychology, emotional support  
  *Smooth, sophisticated, and empathetic delivery.*

- **😂 Peter Griffin** — Comic relief, stress reduction, light-hearted banter  
  *Playful, exaggerated, spontaneous humor.*

---

## 🚀 Core Applications

### 📅 Celebrity Calendar Assistant
```bash
python celebrity_calendar_assistant.py
```
- **Google Calendar Integration** — manage actual events, not mock data
- **Celebrity Voice Announcements** — events narrated with flair
- **Smart Event Management** — create, read, delete, confirm
- **Persistent Conversation History** — builds ongoing context
- **Advanced Task Orchestration** — Portia SDK integration

### 🎥 David Attenborough Webcam Narrator
```bash
python narrator.py
```
- **Live Webcam Analysis** — powered by Google Gemini Vision AI
- **Continuous Documentary Commentary** — builds stories frame by frame
- **Conversation Storage** — JSON-based persistence
- **Auto-save** — reliable progress tracking

### 📧 Celebrity Email Reader
```bash
python celebrity_gmail_reader.py
```
- **Gmail Integration** — reads your real emails securely
- **Celebrity Voice Delivery** — emails with personality
- **Smart Summarization** — insightful, concise, context-aware

---

## 🏗️ Technology Stack

- **AI & Language Models:** Google Gemini 1.5 Flash, Anthropic Claude 3.5 Haiku, OpenAI GPT-4
- **Audio & TTS:** Google Cloud TTS, Journey Voice Collection, pyttsx3 fallback, Pygame playback
- **Integrations:** Portia SDK (multi-agent orchestration), Google Calendar API, Gmail API, Google Cloud Vision
- **Data Management:** JSON-based conversation history, auto-save, error recovery

---

## 🎯 Key Features

- **Multi-Personality System:** Intelligent celebrity selection, voice matching, contextual switching  
- **Premium Audio:** Neural voices, multi-platform support, fast caching  
- **Advanced AI Integration:** Multi-model support, context-aware responses, task orchestration  
- **Real-World Data:** Live calendar/events, secure Gmail, live webcam, persistent sessions

---

## ⚙️ Installation & Setup

### Prerequisites
```bash
python --version         # Python 3.8+ required
python -m venv agent-venv
source agent-venv/bin/activate  # Linux/Mac
agent-venv\Scripts\activate     # Windows
```

### Quick Install
```bash
git clone https://github.com/yashpal2104/agent-hacks-serverless-ai-agent.git
cd agent-hacks-serverless-ai-agent
pip install -r requirements.txt
cp .env.example .env
```

### API Keys Configuration
Edit `.env` with your API keys:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=your_service_account.json
PORTIA_API_KEY=your_portia_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### Google Cloud Setup
1. Create a Google Cloud Project
2. Enable Text-to-Speech API
3. Create a Service Account
4. Download JSON credentials
5. Set `GOOGLE_APPLICATION_CREDENTIALS` path

📚 [Detailed setup guide](GOOGLE_TTS_SETUP.md)

---

## 🎮 Usage Examples

### Calendar Management
```python
# David Attenborough reading your schedule
"Here we observe the fascinating ritual of the 'daily standup meeting'..."

# Morgan Freeman creating events
"And so it was, on this Tuesday morning, that a new meeting was born..."
```

### Webcam Commentary
```python
# David analyzing your workspace
"Note the remarkable eyewear appendages — possibly designed to enhance visual acuity."
```

### Email Reading
```python
# Scarlett reading work emails
"Darling, it seems your boss has some... interesting priorities."

# Peter Griffin on spam
"Holy crap! Someone thinks you've won the Nigerian lottery AGAIN!"
```

---

## 📁 Project Structure

```
📦 agent-hacks-serverless-ai-agent/
├── celebrity_calendar_assistant.py      # Calendar assistant
├── narrator.py                         # Webcam narrator
├── celebrity_gmail_reader.py           # Email reader
├── celebrity_companion_ai_clean.py     # Multi-personality chatbot
├── .env.example                        # Env template
├── requirements.txt                    # Python dependencies
├── GOOGLE_TTS_SETUP.md                 # Setup guide
├── demo_google_tts.py                  # TTS verification
├── celebrity_audio/                    # Sample voices
├── companion_audio/                    # Generated audio
├── frames/                             # Webcam frames
├── *.json                              # Conversation history
├── chat_history.json                   # Persistent logs
├── .portia/                            # Portia config
├── test_*.py                           # Test scripts
├── quick_test.py                       # Quick tests
└── various_demos.py                    # Feature demos
```

---

## 🧠 Advanced Features

- **Persistent Memory:** Conversations across restarts
- **Smart Summarization:** Key points preserved
- **Emotional Intelligence:** Celebrity selection adapts to your mood
- **Performance Optimizations:** Lazy loading, audio caching, efficient memory, graceful fallback
- **Security & Privacy:** Local audio processing, secure API integration, encrypted data, privacy-first design
- **User Experience:** Beautiful CLI, audio-visual feedback, helpful error messages, cross-platform support

---

## 🧪 Demo & Testing

### Quick Tests
```bash
python quick_test.py
python demo_google_tts.py
python test_calendar_data.py
```

### Component Checks
```bash
python -c "from celebrity_calendar_assistant import *; test_voice('david')"
python -c "import google.cloud.texttospeech; print('✅ Google Cloud TTS ready!')"
python -c "from portia import Portia; print('✅ Portia SDK available!')"
```

---

## 🤝 Contributing

We welcome all contributions!

- **Add New Celebrities:**  
  1. Define voice in `celebrity_voices.py`  
  2. Add prompts and test with TTS  
  3. Submit PR with docs and examples

- **Improve Features:**  
  Bug fixes, performance, new integrations, better UX

- **Documentation:**  
  Setup guides, video tutorials, API docs, translations

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Google Cloud, Gemini, Anthropic Claude, Portia SDK** — AI and orchestration
- **David Attenborough, Morgan Freeman, Scarlett Johansson, Seth MacFarlane** — Inspiration
- **Open Source Community** — Libraries, feedback, improvements

---

## 📞 Support & Community

- **Issues:** [GitHub Issues](https://github.com/yashpal2104/agent-hacks-serverless-ai-agent/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yashpal2104/agent-hacks-serverless-ai-agent/discussions)
- **Contact:** [@yashpal2104](https://github.com/yashpal2104) | Email: [Add your email if desired]

---

<div align="center">

**"The future of AI isn’t just artificial intelligence — it’s artificial personality!"**

*Made with ❤️ by the AI Agent Hacks community.*

⭐ **Star this repo to support AI-powered celebrity companions!** ⭐

</div>

---

## 🏁 Quick Start Guide

Get started in 5 minutes:

1. **Clone & Install:**
   ```bash
   git clone https://github.com/yashpal2104/agent-hacks-serverless-ai-agent.git
   cd agent-hacks-serverless-ai-agent
   pip install -r requirements.txt
   ```

2. **Configure API Keys:**
   - Copy `.env.example` to `.env`
   - Add your Google API key and service account

3. **Test Your Setup:**
   ```bash
   python demo_google_tts.py
   ```

4. **Start Exploring:**
   ```bash
   python celebrity_calendar_assistant.py      # Calendar assistant
   python narrator.py                         # Webcam commentary
   python celebrity_companion_ai_clean.py     # General chat
   ```

**Enjoy your flawless AI celebrity experience! 🎉**
