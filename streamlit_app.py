#!/usr/bin/env python3
"""
🎭🚀 Celebrity AI Assistant Suite - Streamlit Frontend
====================================================
Beautiful web interface for all celebrity AI features:
- Live David Attenborough Webcam Narrator
- Celebrity Calendar Assistant with Real Google Calendar
- Multi-Celebrity Companion Chat
- Voice-enabled interactions with Google Cloud TTS
"""

import streamlit as st

# Configure Streamlit page FIRST (before any other st. commands)
st.set_page_config(
    page_title="🎭 Celebrity AI Assistant Suite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import sys
import time
import base64
import tempfile
import threading
from datetime import datetime, timedelta
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import json
import subprocess
from typing import Dict, Any, Optional

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our backend modules
try:
    from narrator import encode_image, analyze_image, play_audio, stop_audio
    NARRATOR_AVAILABLE = True
except ImportError as e:
    st.error(f"Narrator module not available: {e}")
    NARRATOR_AVAILABLE = False

try:
    from gmail_reader import GmailReader
    GMAIL_AVAILABLE = True
    print("✅ Enhanced Gmail reader imported successfully")
except ImportError as e:
    print(f"⚠️ Gmail module not available: {e}")
    GMAIL_AVAILABLE = False

try:
    from celebrity_companion_ai_clean import CelebrityCompanionAI
    COMPANION_AVAILABLE = True
except ImportError as e:
    try:
        # Fallback to simple companion
        from simple_celebrity_companion import CelebrityCompanionAI
        COMPANION_AVAILABLE = True
        st.info("Using simplified celebrity companion (Portia unavailable)")
    except ImportError as e2:
        st.error(f"Celebrity Companion not available: {e2}")
        COMPANION_AVAILABLE = False

try:
    from celebrity_calendar_assistant import CalendarCelebrityVoice, init_portia_calendar, execute_calendar_action_with_portia, generate_calendar_script, setup_content_generator
    CALENDAR_AVAILABLE = True
except ImportError as e:
    st.error(f"Calendar Assistant not available: {e}")
    CALENDAR_AVAILABLE = False

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .celebrity-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .feature-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .chat-user {
        background-color: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-celebrity {
        background-color: #f3e5f5;
        margin-right: auto;
        text-align: left;
    }
    
    .sidebar .stSelectbox {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'companion_ai' not in st.session_state:
    st.session_state.companion_ai = None
if 'calendar_voice' not in st.session_state:
    st.session_state.calendar_voice = None
if 'portia_calendar' not in st.session_state:
    st.session_state.portia_calendar = None
if 'narrator_running' not in st.session_state:
    st.session_state.narrator_running = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_celebrity' not in st.session_state:
    st.session_state.current_celebrity = None
if 'conversation_file' not in st.session_state:
    st.session_state.conversation_file = "streamlit_chat_history.json"

def load_chat_history():
    """Load chat history from file"""
    try:
        if os.path.exists(st.session_state.conversation_file):
            with open(st.session_state.conversation_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

def save_chat_history():
    """Save chat history to file"""
    try:
        with open(st.session_state.conversation_file, 'w') as f:
            json.dump(st.session_state.chat_history, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def init_companion_ai():
    """Initialize the Celebrity Companion AI"""
    if COMPANION_AVAILABLE and st.session_state.companion_ai is None:
        try:
            with st.spinner("🎭 Initializing Celebrity Companion AI..."):
                # Try to import the main companion first
                try:
                    from celebrity_companion_ai_clean import CelebrityCompanionAI
                    st.session_state.companion_ai = CelebrityCompanionAI()
                    st.info("✅ Using full Celebrity Companion AI")
                except Exception as e:
                    # Fall back to simple companion
                    from simple_celebrity_companion import SimpleCelebrityCompanionAI
                    st.session_state.companion_ai = SimpleCelebrityCompanionAI()
                    st.info("✅ Using simplified Celebrity Companion AI (Portia issues)")
                
                st.session_state.chat_history = load_chat_history()
            return True
        except Exception as e:
            st.error(f"Failed to initialize Celebrity Companion AI: {e}")
            return False
    return st.session_state.companion_ai is not None

def init_calendar_system():
    """Initialize the Calendar Assistant"""
    if CALENDAR_AVAILABLE and st.session_state.calendar_voice is None:
        try:
            with st.spinner("📅 Initializing Calendar System..."):
                st.session_state.calendar_voice = CalendarCelebrityVoice()
                
                # Try to initialize Portia with timeout handling
                try:
                    st.session_state.portia_calendar = init_portia_calendar()
                    if st.session_state.portia_calendar:
                        st.success("✅ Calendar system initialized with Portia")
                    else:
                        st.warning("⚠️ Calendar initialized but Portia unavailable (timeout)")
                        st.info("Voice features available, but calendar integration limited")
                except Exception as e:
                    st.warning(f"⚠️ Portia initialization failed: {e}")
                    st.info("Voice features available, but calendar integration limited")
                    st.session_state.portia_calendar = None
                    
            return True
        except Exception as e:
            st.error(f"Failed to initialize Calendar System: {e}")
            return False
    return st.session_state.calendar_voice is not None

def main_header():
    """Display main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎬🤖 Celebrity AI Assistant Suite</h1>
        <p>Transform your digital life with AI-powered celebrity companions!</p>
        <p>📅 Calendar Management | 🎥 Live Commentary | 💬 Celebrity Chat | 🔊 Authentic Voices</p>
    </div>
    """, unsafe_allow_html=True)

def celebrity_selection_sidebar():
    """Celebrity selection in sidebar"""
    st.sidebar.markdown("## 🎭 Celebrity Selection")
    
    celebrities = {
        "david": "🌿 David Attenborough - Nature Wisdom",
        "morgan": "🎬 Morgan Freeman - Deep Philosophy", 
        "scarlett": "🔥 Scarlett Johansson - Modern Psychology",
        "peter": "😂 Peter Griffin - Relatable Humor"
    }
    
    selected = st.sidebar.selectbox(
        "Choose your celebrity companion:",
        options=list(celebrities.keys()),
        format_func=lambda x: celebrities[x],
        index=0
    )
    
    st.session_state.current_celebrity = selected
    return selected

def webcam_narrator_tab():
    """David Attenborough Webcam Narrator"""
    st.markdown("## 🎥 David Attenborough Live Commentary")
    st.markdown("**Experience real-time nature documentary narration of your webcam feed!**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🌟 Features</h3>
            <p>• Live webcam analysis with Google Gemini AI</p>
            <p>• Real-time documentary commentary</p>
            <p>• Context-aware narrative building</p>
            <p>• Authentic British voice with Google Cloud TTS</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Live camera feed
        st.markdown("### 📹 Live Camera Feed")
        
        # Camera controls
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            enable_camera = st.checkbox("📹 Enable Camera", key="enable_camera")
        with col1b:
            auto_analyze = st.checkbox("🔄 Auto-analyze (every 10s)", key="auto_analyze")
        with col1c:
            analyze_now = st.button("� Analyze Now", key="analyze_now")
        
        # Camera feed placeholder
        camera_placeholder = st.empty()
        commentary_placeholder = st.empty()
        
        # Initialize webcam if enabled
        if enable_camera:
            try:
                import cv2
                
                # Initialize camera
                if 'camera' not in st.session_state:
                    st.session_state.camera = cv2.VideoCapture(0)
                
                if st.session_state.camera.isOpened():
                    # Capture frame
                    ret, frame = st.session_state.camera.read()
                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Display frame
                        camera_placeholder.image(frame_rgb, caption="Live Webcam Feed", use_column_width=True)
                        
                        # Save current frame
                        os.makedirs("frames", exist_ok=True)
                        cv2.imwrite("frames/frame.jpg", frame)
                        
                        # Auto-analyze if enabled
                        if auto_analyze:
                            current_time = time.time()
                            if 'last_analysis_time' not in st.session_state:
                                st.session_state.last_analysis_time = 0
                            
                            if current_time - st.session_state.last_analysis_time > 10:  # 10 seconds
                                st.session_state.last_analysis_time = current_time
                                analyze_now = True
                        
                        # Analyze frame if requested
                        if analyze_now and NARRATOR_AVAILABLE:
                            with st.spinner("🎭 Sir David is analyzing..."):
                                try:
                                    # Encode current frame
                                    base64_image = encode_image("frames/frame.jpg")
                                    
                                    # Load conversation history
                                    script = []
                                    if os.path.exists("david_attenborough_commentary.json"):
                                        with open("david_attenborough_commentary.json", 'r') as f:
                                            script = json.load(f)
                                    
                                    # Analyze with context
                                    analysis = analyze_image(base64_image, script)
                                    
                                    # 🎙️ NARRATE the commentary (this was missing!)
                                    try:
                                        # Get voice settings from widget state
                                        voice_speed = st.session_state.get('voice_speed', 1.1)
                                        voice_pitch = st.session_state.get('voice_pitch', -1.0)
                                        play_audio(analysis, speed=voice_speed, pitch=voice_pitch)
                                    except Exception as audio_error:
                                        st.warning(f"🔇 Audio playback failed: {audio_error}")
                                    
                                    # Display result
                                    commentary_placeholder.markdown(f"""
                                    <div class="status-success">
                                        <h4>🎙️ Sir David says:</h4>
                                        <p>{analysis}</p>
                                        <small><em>Analysis timestamp: {datetime.now().strftime('%H:%M:%S')}</em></small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Add to conversation history
                                    new_entry = {
                                        "role": "assistant",
                                        "content": analysis,
                                        "timestamp": time.time(),
                                        "frame": len(script)
                                    }
                                    
                                    script.append(new_entry)
                                    
                                    # Save updated history
                                    with open("david_attenborough_commentary.json", 'w') as f:
                                        json.dump(script, f, indent=2)
                                    
                                    # Auto-refresh for continuous analysis
                                    if auto_analyze:
                                        time.sleep(1)
                                        st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Analysis failed: {e}")
                    else:
                        camera_placeholder.error("❌ Could not capture frame from camera")
                else:
                    camera_placeholder.error("❌ Could not open camera")
                    
            except ImportError:
                camera_placeholder.error("❌ OpenCV not available - cannot access camera")
            except Exception as e:
                camera_placeholder.error(f"❌ Camera error: {e}")
        
        else:
            camera_placeholder.info("📹 Enable camera to start live commentary")
            
            # Manual frame analysis option
            uploaded_file = st.file_uploader("📸 Or upload an image for analysis", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Save for analysis
                os.makedirs("frames", exist_ok=True)
                image.save("frames/frame.jpg")
                
                if st.button("🔍 Analyze Uploaded Image"):
                    if NARRATOR_AVAILABLE:
                        with st.spinner("🎭 Sir David is analyzing your image..."):
                            try:
                                base64_image = encode_image("frames/frame.jpg")
                                
                                # Load conversation history
                                script = []
                                if os.path.exists("david_attenborough_commentary.json"):
                                    with open("david_attenborough_commentary.json", 'r') as f:
                                        script = json.load(f)
                                
                                analysis = analyze_image(base64_image, script)
                                
                                # 🎙️ NARRATE the commentary (this was missing!)
                                try:
                                    # Get voice settings from widget state
                                    voice_speed = st.session_state.get('voice_speed', 1.1)
                                    voice_pitch = st.session_state.get('voice_pitch', -1.0)
                                    play_audio(analysis, speed=voice_speed, pitch=voice_pitch)
                                except Exception as audio_error:
                                    st.warning(f"🔇 Audio playback failed: {audio_error}")
                                
                                commentary_placeholder.markdown(f"""
                                <div class="status-success">
                                    <h4>🎙️ Sir David says:</h4>
                                    <p>{analysis}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            except Exception as e:
                                st.error(f"Analysis failed: {e}")
    
    with col2:
        st.markdown("### 🎙️ Sir David's Voice Settings")
        
        # Voice settings - store in session state for use during narration
        voice_speed = st.slider("Speech Rate", 0.5, 1.5, 1.1, 0.1, key='voice_speed')
        voice_pitch = st.slider("Pitch Adjustment", -5.0, 5.0, -1.0, 0.5, key='voice_pitch')
        
        # Voice preview button
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("🎙️ Test Voice Settings"):
                if NARRATOR_AVAILABLE:
                    test_text = "Hello! This is Sir David Attenborough speaking with your current voice settings. Fascinating isn't it?"
                    try:
                        play_audio(test_text, speed=voice_speed, pitch=voice_pitch)
                        st.success("🔊 Voice test played!")
                    except Exception as e:
                        st.error(f"Voice test failed: {e}")
                else:
                    st.warning("Narrator not available for voice testing")
        
        with col2b:
            if st.button("⏹️ Stop Audio"):
                if NARRATOR_AVAILABLE:
                    try:
                        stop_audio()
                        st.success("⏹️ Audio stopped!")
                    except Exception as e:
                        st.error(f"Stop failed: {e}")
                else:
                    st.warning("No audio system available")
        
        st.markdown("### 📝 Live Commentary History")
        
        # Load and display conversation history
        if os.path.exists("david_attenborough_commentary.json"):
            try:
                with open("david_attenborough_commentary.json", 'r') as f:
                    commentary_history = json.load(f)
                
                st.write(f"**{len(commentary_history)} observations saved**")
                
                if commentary_history:
                    # Show most recent entries
                    st.markdown("**Recent Live Commentary:**")
                    for i, entry in enumerate(commentary_history[-3:]):
                        timestamp = entry.get('timestamp', 0)
                        if timestamp:
                            time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
                        else:
                            time_str = "Unknown"
                        
                        with st.expander(f"🎬 Frame {entry.get('frame', i)} at {time_str}"):
                            content = entry['content']
                            st.write(content[:300] + "..." if len(content) > 300 else content)
                
                # Clear history option
                if st.button("🗑️ Clear Commentary History"):
                    os.remove("david_attenborough_commentary.json")
                    st.success("Commentary history cleared!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error loading commentary history: {e}")
        else:
            st.info("No commentary history yet. Enable camera and start analyzing!")
        
        # System status
        st.markdown("### 📊 System Status")
        
        # Check camera status
        camera_status = "⏸️"  # Default: not initialized
        if 'camera' in st.session_state:
            if hasattr(st.session_state.camera, 'isOpened') and st.session_state.camera.isOpened():
                camera_status = "✅"
            else:
                camera_status = "❌"
        
        status_items = [
            ("🎥 Camera Access", camera_status),
            ("🧠 Narrator AI", "✅" if NARRATOR_AVAILABLE else "❌"),
            ("📁 Frame Directory", "✅" if os.path.exists("frames") else "❌"),
            ("💾 Auto-save", "✅" if os.path.exists("david_attenborough_commentary.json") else "⏸️")
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}:** {status}")
    
    # Cleanup camera on disable
    if not enable_camera and 'camera' in st.session_state:
        if st.session_state.camera.isOpened():
            st.session_state.camera.release()
        del st.session_state.camera

def gmail_reader_tab():
    """Enhanced Celebrity Gmail Email Reader & Summarizer"""
    st.markdown("## 📧 Enhanced Celebrity Gmail Reader")
    st.markdown("**🎭 Natural celebrity voices with task-based Portia integration!**")
    
    if not GMAIL_AVAILABLE:
        st.error("❌ Enhanced Gmail reader not available. Please check dependencies.")
        st.markdown("""
        **To enable the enhanced Gmail reader:**
        1. Ensure `task_based_celebrity_gmail.py` exists with your enhanced implementation
        2. Install required dependencies: `pip install portia google-cloud-texttospeech`
        3. Set up Google Cloud TTS credentials if available
        """)
        return
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📬 Enhanced Gmail Analysis")
        st.markdown("*Using task-based Portia approach with natural celebrity voices*")
        
        # Gmail connection status
        gmail_status_placeholder = st.empty()
        
        # Email input settings
        st.markdown("### 🎛️ Email Settings")
        
        col1a, col1b = st.columns(2)
        with col1a:
            sender_email = st.text_input(
                "📧 Sender Email (optional)", 
                placeholder="e.g., john@company.com",
                help="Leave blank to analyze all recent emails"
            )
        with col1b:
            max_emails = st.slider("Max Emails to Analyze", 5, 50, 20)
        
        # Celebrity selection with your improved lineup
        email_celebrity = st.selectbox(
            "🎭 Choose Celebrity Email Reader:",
            ["David Attenborough", "Morgan Freeman", "Scarlett Johansson", "Peter Griffin"],
            key="email_celebrity_enhanced",
            help="Each celebrity has unique natural voice characteristics"
        )
        
        # Voice settings
        st.markdown("### 🎙️ Voice Settings")
        col1a, col1b = st.columns(2)
        with col1a:
            voice_speed = st.slider("🎶 Speaking Speed", 0.5, 2.0, 1.0, 0.1)
        with col1b:
            voice_pitch = st.slider("🎵 Voice Pitch", -5.0, 5.0, 0.0, 0.5)
        
        # Enhanced Gmail authentication and analysis
        col1a, col1b, col1c = st.columns(3)
        
        with col1a:
            if st.button("📧 Read Gmail (Enhanced)", type="primary"):
                gmail_status_placeholder.markdown("""
                <div class="status-info">
                    <h4>🔄 Initializing Enhanced Gmail Reader...</h4>
                    <p>Using task-based Portia integration with wrapper</p>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    # Initialize enhanced Gmail reader wrapper
                    with st.spinner("🎙️ Setting up enhanced Gmail reader..."):
                        gmail_reader = GmailReader()
                    
                    # Authenticate with Portia
                    gmail_status_placeholder.markdown("""
                    <div class="status-info">
                        <h4>🔧 Authenticating with Enhanced Portia...</h4>
                        <p>Task-based Gmail access setup</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if gmail_reader.authenticate_with_portia():
                        gmail_status_placeholder.markdown("""
                        <div class="status-success">
                            <h4>✅ Enhanced Portia Gmail Connected!</h4>
                            <p>Fetching emails with task-based approach...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Fetch emails using enhanced wrapper method
                        with st.spinner(f"🔍 {email_celebrity} is analyzing your emails with enhanced AI..."):
                            emails = gmail_reader.get_emails_with_portia(
                                sender_email=sender_email.strip() if sender_email.strip() else None,
                                max_results=max_emails
                            )
                            
                            if emails:
                                # Generate enhanced celebrity summary using wrapper
                                summary = gmail_reader.summarize_emails_with_celebrity(
                                    emails, email_celebrity
                                )
                                
                                # Display results
                                gmail_status_placeholder.markdown(f"""
                                <div class="status-success">
                                    <h4>🎭 {email_celebrity}'s Enhanced Email Analysis:</h4>
                                    <p>Using natural voice characteristics and personality traits</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Show enhanced script preview
                                with st.expander(f"📜 {email_celebrity}'s Enhanced Script", expanded=True):
                                    st.markdown(f"""
                                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                                        <p style="font-size: 1.1em; line-height: 1.6; font-style: italic;">
                                            {summary}
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Store for voice playback
                                st.session_state['current_email_summary'] = summary
                                st.session_state['current_email_celebrity'] = email_celebrity
                                st.session_state['gmail_reader'] = gmail_reader
                                
                                # Store in history
                                if 'email_history' not in st.session_state:
                                    st.session_state.email_history = []
                                
                                st.session_state.email_history.append({
                                    'timestamp': datetime.now(),
                                    'celebrity': email_celebrity,
                                    'summary': summary[:200] + "...",
                                    'email_count': len(emails)
                                })
                                
                                st.success(f"✅ Enhanced analysis complete! {len(emails)} emails processed.")
                                
                            else:
                                st.warning("📪 No recent emails found via enhanced Portia integration.")
                                
                    else:
                        gmail_status_placeholder.markdown("""
                        <div class="status-error">
                            <h4>❌ Enhanced Portia Setup Failed</h4>
                            <p>Please check Portia configuration and try again</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    gmail_status_placeholder.markdown(f"""
                    <div class="status-error">
                        <h4>❌ Enhanced Gmail Reading Failed</h4>
                        <p>Error: {str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.error(f"Detailed error: {e}")
        
        with col1b:
            # Enhanced voice playback using wrapper
            if st.button("🔊 Play Enhanced Voice", type="secondary"):
                if ('current_email_summary' in st.session_state and 
                    'gmail_reader' in st.session_state):
                    
                    summary = st.session_state['current_email_summary']
                    celebrity = st.session_state['current_email_celebrity']
                    gmail_reader = st.session_state['gmail_reader']
                    
                    with st.spinner(f"🎙️ {celebrity} is speaking with enhanced natural voice..."):
                        try:
                            success = gmail_reader.speak_email_summary(summary, celebrity)
                            if success:
                                st.success(f"✅ {celebrity} finished speaking with enhanced voice!")
                            else:
                                st.info(f"📝 {celebrity}'s message displayed as text (enhanced voice unavailable)")
                        except Exception as e:
                            st.error(f"Enhanced voice playback error: {e}")
                            st.markdown(f"**🗣️ {celebrity} says:**")
                            st.markdown(f"> {summary}")
                else:
                    st.warning("⚠️ No email analysis available. Please read Gmail first.")
        
        with col1c:
            # Stop enhanced narration using wrapper
            if st.button("⏹️ Stop Enhanced Voice", type="secondary"):
                if 'gmail_reader' in st.session_state:
                    st.session_state['gmail_reader'].stop_narration()
                    st.info("⏹️ Enhanced voice playback stopped")
                else:
                    st.warning("No active enhanced voice to stop")
    
    with col2:
        # Enhanced sidebar info
        st.markdown("### 🎭 Celebrity Voice Features")
        
        if email_celebrity == "David Attenborough":
            st.markdown("""
            **🇬🇧 Sir David Attenborough**
            - *Gentle, breathy British accent*
            - *Nature documentary style*  
            - *Scientific curiosity*
            - *Premium Google TTS: en-GB-Journey-D*
            """)
        elif email_celebrity == "Morgan Freeman":
            st.markdown("""
            **🎬 Morgan Freeman**
            - *Deep, resonant narration*
            - *Dramatic pauses*
            - *Philosophical insights*
            - *Premium Google TTS: en-US-Journey-D*
            """)
        elif email_celebrity == "Scarlett Johansson":
            st.markdown("""
            **🎭 Scarlett Johansson**
            - *Smooth, slightly husky voice*
            - *Calm confidence*
            - *Thoughtful analysis*
            - *Premium Google TTS: en-US-Journey-F*
            """)
        elif email_celebrity == "Peter Griffin":
            st.markdown("""
            **� Peter Griffin**
            - *High-pitched, cartoonish*
            - *Humorous commentary*
            - *Genuine moments*
            - *Premium Google TTS: en-US-Casual-K*
            """)
        
        st.markdown("---")
        st.markdown("### 🚀 Enhanced Features")
        st.markdown("""
        - **🎙️ Premium Google Cloud TTS**
        - **🔧 Task-based Portia integration**
        - **🎭 Authentic celebrity voices**
        - **📧 Natural email conversation**
        - **⚡ Smart authentication flow**
        - **🎛️ Voice speed & pitch control**
        """)
        
        # Email history
        if 'email_history' in st.session_state and st.session_state.email_history:
            st.markdown("### 📜 Recent Email Readings")
            for entry in reversed(st.session_state.email_history[-3:]):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0;">
                    <small><strong>{entry['celebrity']}</strong><br>
                    {entry['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col1b:
            # Narration controls
            if 'current_email_summary' in st.session_state:
                if st.button("🎙️ Start Narration", type="secondary"):
                    try:
                        gmail_reader = st.session_state.get('gmail_reader')
                        if gmail_reader:
                            voice_speed = st.session_state.get('email_voice_speed', 1.0)
                            voice_pitch = st.session_state.get('email_voice_pitch', 0.0)
                            
                            with st.spinner(f"🎬 {st.session_state['current_email_celebrity']} is speaking..."):
                                gmail_reader.speak_email_summary(
                                    st.session_state['current_email_summary'],
                                    st.session_state['current_email_celebrity'],
                                    speed=voice_speed,
                                    pitch=voice_pitch
                                )
                            st.success("🔊 Email narration completed!")
                        else:
                            st.error("Gmail reader not available for narration")
                    except Exception as e:
                        st.error(f"Narration failed: {e}")
                
                if st.button("⏹️ Stop Narration", type="secondary"):
                    try:
                        gmail_reader = st.session_state.get('gmail_reader')
                        if gmail_reader:
                            gmail_reader.stop_narration()
                            st.success("⏹️ Narration stopped!")
                        else:
                            st.warning("No active narration to stop")
                    except Exception as e:
                        st.error(f"Stop failed: {e}")
        
        # Quick email actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Refresh Email Analysis"):
            st.rerun()
        
        # Gmail setup instructions
        with st.expander("📝 Gmail Setup Instructions"):
            st.markdown("""
            **To enable Gmail reading with Portia:**
            
            1. **Portia Setup:**
               - Ensure Portia SDK is installed: `pip install portia`
               - Portia will handle Gmail authentication automatically
               - No additional Google Cloud Console setup needed
               
            2. **Authentication Flow:**
               - Click "Read My Gmail" button
               - Portia will guide you through OAuth authentication
               - Complete the authentication in your browser
               - Gmail access will be handled via Portia tools
               
            3. **Supported Features:**
               - Recent email analysis with celebrity voices
               - Natural voice narration with start/stop controls
               - Email summaries with personality-based insights
               
            4. **Celebrities Available:**
               - **David Attenborough**: Nature documentary style
               - **Morgan Freeman**: Deep, philosophical narration  
               - **Scarlett Johansson**: Modern, sophisticated voice
               - **Peter Griffin**: Humorous Family Guy style
               
            5. **Voice Controls:**
               - Start/Stop narration buttons
               - Voice speed and pitch adjustments
               - Natural Google Cloud TTS voices
            """)
    
    with col2:
        st.markdown("### 🎙️ Email Voice Settings")
        
        # Voice settings (reuse from narrator)
        voice_speed = st.slider("Email Speech Rate", 0.5, 1.5, 1.0, 0.1, key='email_voice_speed')
        voice_pitch = st.slider("Email Pitch", -5.0, 5.0, -1.0, 0.5, key='email_voice_pitch')
        
        # Voice preview for emails
        if st.button("🎙️ Test Email Voice"):
            test_text = f"Hello! This is {st.session_state.get('email_celebrity', 'David Attenborough')} reading your email summary with these voice settings."
            try:
                play_audio(test_text, speed=voice_speed, pitch=voice_pitch)
                st.success("🔊 Voice test played!")
            except Exception as e:
                st.error(f"Voice test failed: {e}")
        
        st.markdown("### 📊 Email Analysis History")
        
        # Display email analysis history
        if 'email_history' in st.session_state and st.session_state.email_history:
            st.write(f"**{len(st.session_state.email_history)} analyses completed**")
            
            # Show recent analyses
            for i, analysis in enumerate(st.session_state.email_history[-3:]):
                timestamp = analysis['timestamp'].strftime('%H:%M:%S')
                with st.expander(f"📧 {analysis['celebrity']} at {timestamp}"):
                    st.write(f"**Emails analyzed:** {analysis['email_count']}")
                    summary_preview = analysis['summary'][:200] + "..." if len(analysis['summary']) > 200 else analysis['summary']
                    st.write(summary_preview)
                    
                    # Replay audio button
                    if st.button(f"🔊 Replay Analysis {i+1}", key=f"replay_{i}"):
                        try:
                            play_audio(analysis['summary'], speed=voice_speed, pitch=voice_pitch)
                            st.success("🔊 Email analysis replayed!")
                        except Exception as e:
                            st.error(f"Replay failed: {e}")
            
            # Clear history button
            if st.button("🗑️ Clear Email History"):
                st.session_state.email_history = []
                st.success("Email history cleared!")
                st.rerun()
        else:
            st.info("No email analyses yet. Click 'Read My Gmail' to start!")
        
        # System status
        st.markdown("### 📊 Gmail System Status")
        
        gmail_status_items = [
            ("📧 Gmail Reader", "✅" if GMAIL_AVAILABLE else "❌"),
            ("🤖 Portia Tools", "✅" if 'portia' in sys.modules else "❌"),
            ("🎙️ Voice Synthesis", "✅" if NARRATOR_AVAILABLE else "❌"),
            ("� Natural Voices", "✅" if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else "⏸️")
        ]
        
        for item, status in gmail_status_items:
            st.markdown(f"**{item}:** {status}")

def calendar_assistant_tab():
    """Celebrity Calendar Assistant"""
    st.markdown("## 📅 Celebrity Calendar Assistant")
    st.markdown("**Manage your Google Calendar with celebrity voices reading your REAL events!**")
    
    # Initialize calendar system
    if not init_calendar_system():
        st.error("❌ Calendar system not available")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Calendar Operations")
        
        # Calendar action selection
        action = st.selectbox(
            "Choose calendar action:",
            [
                "get events",
                "today events", 
                "tomorrow events",
                "check availability",
                "create event",
                "delete event"
            ],
            format_func=lambda x: {
                "get events": "📅 View upcoming events",
                "today events": "📆 Today's schedule",
                "tomorrow events": "📅 Tomorrow's events", 
                "check availability": "🕐 Check availability",
                "create event": "➕ Create new event",
                "delete event": "🗑️ Delete event"
            }.get(x, x)
        )
        
        # Additional details for create/delete
        details = ""
        if action in ["create event", "delete event"]:
            details = st.text_input(
                f"Event details for {action}:",
                placeholder="Enter event name/description"
            )
        
        # Celebrity voice selection for calendar
        calendar_celebrity = st.selectbox(
            "Choose celebrity voice:",
            ["David Attenborough", "Morgan Freeman", "Scarlett Johansson", "Peter Griffin"]
        )
        
        # Execute calendar action
        if st.button("🎭 Execute with Celebrity Voice", key="calendar_execute"):
            if st.session_state.portia_calendar is None:
                st.warning("❌ Real calendar access unavailable (Portia timeout)")
                st.info("🎭 Demonstrating celebrity voice with sample calendar data")
                
                # Demo calendar data
                demo_calendar_data = {
                    "get events": "You have 3 upcoming events: 1) Team standup meeting at 9:00 AM tomorrow, 2) Project review at 2:00 PM on Wednesday, 3) Client presentation on Friday at 10:00 AM.",
                    "today events": f"Today is {datetime.now().strftime('%B %d, %Y')}. You have a team meeting at 10:00 AM and lunch with Sarah at 12:30 PM.",
                    "tomorrow events": f"Tomorrow you have: Morning standup at 9:00 AM, Design review at 2:00 PM, and Gym session at 6:00 PM.",
                    "check availability": "You are free from 10:00 AM to 12:00 PM today, and from 3:00 PM to 5:00 PM tomorrow.",
                    "create event": f"I've created a sample event: '{details}' scheduled for tomorrow at 2:00 PM." if details else "I've created a sample meeting for tomorrow at 2:00 PM.",
                    "delete event": f"I've deleted the event: '{details}' from your calendar." if details else "I've deleted the selected event from your calendar."
                }
                
                result = demo_calendar_data.get(action, "Sample calendar operation completed.")
                
                with st.spinner(f"🎭 {calendar_celebrity} is preparing your response..."):
                    # Generate celebrity response
                    content_model = setup_content_generator()
                    if content_model:
                        script = generate_calendar_script(
                            content_model,
                            calendar_celebrity,
                            action,
                            result,
                            st.session_state.calendar_voice
                        )
                    else:
                        script = f"Hello! This is {calendar_celebrity}. {result}"
                    
                    # Display celebrity response
                    st.markdown(f"""
                    <div class="celebrity-card">
                        <h4>🎭 {calendar_celebrity} says:</h4>
                        <p>{script}</p>
                        <small><em>Demo mode - not connected to real calendar</em></small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Play voice if available
                    if st.session_state.calendar_voice:
                        try:
                            st.session_state.calendar_voice.speak_calendar_event(script, calendar_celebrity)
                            st.info("🔊 Audio played through system speakers")
                        except Exception as e:
                            st.warning(f"Voice playback failed: {e}")
                
                return
                
            with st.spinner(f"📅 {calendar_celebrity} is accessing your calendar..."):
                try:
                    # Execute calendar action
                    result = execute_calendar_action_with_portia(
                        st.session_state.portia_calendar,
                        action,
                        details
                    )
                    
                    if result:
                        st.success("✅ Calendar action completed!")
                        
                        # Generate celebrity response
                        content_model = setup_content_generator()
                        script = generate_calendar_script(
                            content_model,
                            calendar_celebrity,
                            action,
                            result,
                            st.session_state.calendar_voice
                        )
                        
                        # Display celebrity response
                        st.markdown(f"""
                        <div class="celebrity-card">
                            <h4>🎭 {calendar_celebrity} says:</h4>
                            <p>{script}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Play voice if available
                        if st.session_state.calendar_voice:
                            try:
                                st.session_state.calendar_voice.speak_calendar_event(script, calendar_celebrity)
                                st.info("🔊 Audio played through system speakers")
                            except Exception as e:
                                st.warning(f"Voice playback failed: {e}")
                        
                        # Show raw calendar data
                        with st.expander("📊 Raw Calendar Data"):
                            st.text(result)
                    else:
                        st.error("❌ No calendar data received")
                        
                except Exception as e:
                    st.error(f"Calendar action failed: {e}")
    
    with col2:
        st.markdown("### 🔊 Voice Settings")
        
        # Voice configuration
        st.markdown("**Celebrity Voice Characteristics:**")
        if calendar_celebrity == "David Attenborough":
            st.markdown("🌿 **Nature documentarian** - Gentle, awe-inspired British tone")
        elif calendar_celebrity == "Morgan Freeman":
            st.markdown("🎬 **Wise narrator** - Deep, resonant with dramatic pauses")
        elif calendar_celebrity == "Scarlett Johansson":
            st.markdown("🔥 **Modern sophistication** - Smooth, slightly husky warmth")
        elif calendar_celebrity == "Peter Griffin":
            st.markdown("😂 **Comedy relief** - Playful, exaggerated with laughter")
        
        st.markdown("### 📈 System Status")
        
        # System status
        status_items = [
            ("Google Cloud TTS", "✅" if st.session_state.calendar_voice else "❌"),
            ("Portia SDK", "✅" if st.session_state.portia_calendar else "❌"), 
            ("Calendar Access", "✅" if st.session_state.portia_calendar else "❌"),
            ("Audio System", "✅" if st.session_state.calendar_voice and st.session_state.calendar_voice else "❌")
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}:** {status}")
        
        st.markdown("### 📚 Quick Actions")
        
        quick_actions = [
            ("📅 Today's Events", "today events", ""),
            ("📆 Tomorrow's Events", "tomorrow events", ""),
            ("🕐 Check Free Time", "check availability", ""),
            ("📋 All Upcoming", "get events", "")
        ]
        
        for label, action_type, detail in quick_actions:
            if st.button(label, key=f"quick_{action_type}"):
                # Quick execute
                with st.spinner(f"{calendar_celebrity} checking calendar..."):
                    try:
                        result = execute_calendar_action_with_portia(
                            st.session_state.portia_calendar,
                            action_type,
                            detail
                        )
                        
                        if result:
                            st.success(f"✅ {label} completed")
                            with st.expander("Results"):
                                st.text(result[:500] + "..." if len(result) > 500 else result)
                    except Exception as e:
                        st.error(f"Quick action failed: {e}")

def celebrity_chat_tab():
    """Celebrity Companion Chat"""
    st.markdown("## 💬 Celebrity Companion Chat")
    st.markdown("**Have natural conversations with AI celebrities for emotional support and entertainment!**")
    
    # Initialize companion AI
    if not init_companion_ai():
        st.error("❌ Celebrity Companion AI not available")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💭 Chat Interface")
        
        # Chat history display
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
                if message.startswith("User:"):
                    st.markdown(f"""
                    <div class="chat-message chat-user">
                        <strong>You:</strong> {message[5:].strip()}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Extract celebrity name and message
                    if ":" in message:
                        celebrity_name, msg = message.split(":", 1)
                        st.markdown(f"""
                        <div class="chat-message chat-celebrity">
                            <strong>🎭 {celebrity_name.strip()}:</strong> {msg.strip()}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        user_input = st.text_area(
            "💬 Your message:",
            height=100,
            placeholder="Type your message here... I'll automatically select the best celebrity for you!"
        )
        
        col1a, col1b, col1c = st.columns([2, 1, 1])
        with col1a:
            send_message = st.button("🚀 Send Message", key="send_chat")
        with col1b:
            clear_history = st.button("🗑️ Clear History", key="clear_chat")
        with col1c:
            voice_enabled = st.checkbox("🔊 Enable Voice", value=True)
        
        # Handle message sending
        if send_message and user_input.strip():
            with st.spinner("🎭 Celebrity is thinking..."):
                try:
                    # Get celebrity response
                    response = st.session_state.companion_ai.chat(user_input.strip())
                    
                    # Add to session state
                    st.session_state.chat_history.append(f"User: {user_input.strip()}")
                    st.session_state.chat_history.append(response)
                    
                    # Save to file
                    save_chat_history()
                    
                    # Play voice if enabled
                    if voice_enabled and hasattr(st.session_state.companion_ai, 'speak_text'):
                        try:
                            st.session_state.companion_ai.speak_text(response.split(":", 1)[1] if ":" in response else response)
                        except Exception as e:
                            st.warning(f"Voice playback failed: {e}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Chat failed: {e}")
        
        # Clear history
        if clear_history:
            st.session_state.chat_history = []
            save_chat_history()
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        st.markdown("### 🎭 Celebrity Info")
        
        # Current celebrity info
        if st.session_state.companion_ai and st.session_state.companion_ai.current_celebrity:
            current_celeb = st.session_state.companion_ai.current_celebrity
            celeb_info = st.session_state.companion_ai.celebrities[current_celeb]
            
            st.markdown(f"""
            <div class="celebrity-card">
                <h4>Currently Active: {celeb_info['name']}</h4>
                <p><strong>Personality:</strong> {celeb_info['personality']}</p>
                <p><strong>Style:</strong> {celeb_info['style']}</p>
                <p><strong>Specialties:</strong> {', '.join(celeb_info['specialties'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🧠 AI Selection Logic")
        st.markdown("""
        **The AI automatically selects celebrities based on:**
        - **Anxiety/Stress** → David Attenborough (calming nature)
        - **Sadness/Grief** → Morgan Freeman (deep comfort) 
        - **Anger/Frustration** → Scarlett Johansson (emotional intelligence)
        - **General/Humor** → Peter Griffin (relatable fun)
        """)
        
        st.markdown("### 🔧 Manual Override")
        
        # Manual celebrity switching
        celebrity_override = st.selectbox(
            "Force switch to:",
            ["Auto-Select"] + list(st.session_state.companion_ai.celebrities.keys()) if st.session_state.companion_ai else ["Auto-Select"],
            format_func=lambda x: {
                "Auto-Select": "🤖 Smart Selection",
                "david": "🌿 David Attenborough",
                "morgan": "🎬 Morgan Freeman", 
                "scarlett": "🔥 Scarlett Johansson",
                "peter": "😂 Peter Griffin"
            }.get(x, x)
        )
        
        if celebrity_override != "Auto-Select":
            if st.button("🔄 Switch Celebrity"):
                if st.session_state.companion_ai:
                    st.session_state.companion_ai.current_celebrity = celebrity_override
                    st.success(f"Switched to {st.session_state.companion_ai.celebrities[celebrity_override]['name']}")
                    st.rerun()
        
        st.markdown("### 📊 Chat Statistics")
        
        if st.session_state.chat_history:
            total_messages = len(st.session_state.chat_history)
            user_messages = len([msg for msg in st.session_state.chat_history if msg.startswith("User:")])
            celebrity_messages = total_messages - user_messages
            
            st.markdown(f"""
            - **Total Messages:** {total_messages}
            - **Your Messages:** {user_messages}
            - **Celebrity Responses:** {celebrity_messages}
            """)

def settings_tab():
    """Settings and Configuration"""
    st.markdown("## ⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔑 API Configuration")
        
        # API Keys (masked for security)
        google_api = os.getenv('GOOGLE_API_KEY', '')
        google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        portia_api = os.getenv('PORTIA_API_KEY', '')
        
        st.markdown(f"""
        **Google API Key:** {'✅ Configured' if google_api and google_api != 'dummy_key_for_testing' else '❌ Not configured'}
        
        **Google Cloud Credentials:** {'✅ Configured' if google_creds else '❌ Not configured'}
        
        **Portia API Key:** {'✅ Configured' if portia_api else '❌ Not configured'}
        """)
        
        if st.button("🔄 Reload Environment"):
            from dotenv import load_dotenv
            load_dotenv(override=True)
            st.success("Environment variables reloaded!")
        
        st.markdown("### 🎵 Audio Settings")
        
        # Audio system checks
        audio_systems = []
        try:
            result = subprocess.run(['which', 'paplay'], capture_output=True, text=True)
            if result.returncode == 0:
                audio_systems.append("PulseAudio (paplay)")
        except:
            pass
        
        try:
            result = subprocess.run(['which', 'aplay'], capture_output=True, text=True)
            if result.returncode == 0:
                audio_systems.append("ALSA (aplay)")
        except:
            pass
        
        try:
            import pygame
            audio_systems.append("Pygame")
        except:
            pass
        
        st.markdown("**Available Audio Systems:**")
        for system in audio_systems:
            st.markdown(f"✅ {system}")
        
        if not audio_systems:
            st.markdown("❌ No audio systems detected")
    
    with col2:
        st.markdown("### 📊 System Status")
        
        # Module availability
        modules = [
            ("Narrator Module", NARRATOR_AVAILABLE),
            ("Celebrity Companion", COMPANION_AVAILABLE),
            ("Calendar Assistant", CALENDAR_AVAILABLE),
            ("Google Cloud TTS", 'google.cloud.texttospeech' in sys.modules),
            ("Streamlit", True),
            ("OpenCV", 'cv2' in sys.modules),
            ("Pygame", 'pygame' in sys.modules)
        ]
        
        for module, available in modules:
            status = "✅" if available else "❌"
            st.markdown(f"**{module}:** {status}")
        
        st.markdown("### 🗂️ File Management")
        
        # File operations
        files_to_check = [
            ("narrator.py", "Webcam Narrator"),
            ("celebrity_companion_ai_clean.py", "Celebrity Companion"),
            ("celebrity_calendar_assistant.py", "Calendar Assistant"),
            ("david_attenborough_commentary.json", "Commentary History"),
            ("streamlit_chat_history.json", "Chat History"),
            (".env", "Environment Config")
        ]
        
        st.markdown("**Project Files:**")
        for filename, description in files_to_check:
            exists = os.path.exists(filename)
            status = "✅" if exists else "❌"
            st.markdown(f"**{description}:** {status}")
        
        # Clear data options
        st.markdown("### 🧹 Data Management")
        
        if st.button("🗑️ Clear Commentary History"):
            if os.path.exists("david_attenborough_commentary.json"):
                os.remove("david_attenborough_commentary.json")
                st.success("Commentary history cleared!")
            else:
                st.info("No commentary history to clear")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            if os.path.exists(st.session_state.conversation_file):
                os.remove(st.session_state.conversation_file)
            st.success("Chat history cleared!")
        
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🔧 Test All Systems"):
            with st.spinner("Testing all systems..."):
                results = []
                
                # Test companion AI
                if init_companion_ai():
                    results.append("✅ Celebrity Companion AI: Working")
                else:
                    results.append("❌ Celebrity Companion AI: Failed")
                
                # Test calendar
                if init_calendar_system():
                    results.append("✅ Calendar System: Working") 
                else:
                    results.append("❌ Calendar System: Failed")
                
                # Test narrator
                if NARRATOR_AVAILABLE:
                    results.append("✅ Webcam Narrator: Available")
                else:
                    results.append("❌ Webcam Narrator: Not Available")
                
                for result in results:
                    if "✅" in result:
                        st.success(result)
                    else:
                        st.error(result)

def main():
    """Main Streamlit App"""
    
    # Main header
    main_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # App selection
        app_mode = st.selectbox(
            "🎬 Choose Celebrity AI Feature:",
            [
                "🎥 Webcam Narrator", 
                "� Gmail Reader",
                "�📅 Calendar Assistant",
                "💬 Celebrity Chat", 
                "⚙️ Settings"
            ]
        )
        
        # Celebrity selection for relevant modes
        if app_mode in ["💬 Celebrity Chat", "📅 Calendar Assistant"]:
            celebrity_selection_sidebar()
        
        st.markdown("---")
        
        # Quick status
        st.markdown("### 📊 Quick Status")
        st.markdown(f"**Narrator:** {'🟢 Available' if NARRATOR_AVAILABLE else '🔴 Unavailable'}")
        st.markdown(f"**Gmail Reader:** {'🟢 Available' if GMAIL_AVAILABLE else '🔴 Unavailable'}")
        st.markdown(f"**Companion:** {'🟢 Ready' if COMPANION_AVAILABLE else '🔴 Unavailable'}")
        st.markdown(f"**Calendar:** {'🟢 Ready' if CALENDAR_AVAILABLE else '🔴 Unavailable'}")
        
        st.markdown("---")
        
        # Links and info
        st.markdown("### 🔗 Quick Links")
        st.markdown("[📚 Project README](./README.md)")
        st.markdown("[🐙 GitHub Repository](https://github.com/yashpal2104/agent-hacks-serverless-ai-agent)")
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - **First time?** Check Settings tab for configuration
        - **No audio?** Check your system speakers
        - **Gmail setup?** Download credentials.json from Google Cloud Console
        - **Calendar issues?** Verify Google API credentials
        - **Chat not working?** Ensure Google API key is set
        """)
    
    # Main content area based on selected mode
    if app_mode == "🎥 Webcam Narrator":
        webcam_narrator_tab()
    elif app_mode == "� Gmail Reader":
        gmail_reader_tab()
    elif app_mode == "�📅 Calendar Assistant":
        calendar_assistant_tab()
    elif app_mode == "💬 Celebrity Chat":
        celebrity_chat_tab()
    elif app_mode == "⚙️ Settings":
        settings_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🎭 <strong>Celebrity AI Assistant Suite</strong> - Bringing AI personalities to life!</p>
        <p>Made with ❤️ using Streamlit, Google AI, and Portia SDK</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
