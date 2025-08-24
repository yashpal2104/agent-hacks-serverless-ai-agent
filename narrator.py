import os
import google.generativeai as genai
import base64
import json
import time
import errno
from dotenv import load_dotenv

# Try to import ElevenLabs (optional)
try:
    from elevenlabs import generate, play, set_api_key, voices
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️ ElevenLabs not installed - using text-only mode")

# Try to import system TTS as fallback
try:
    import pyttsx3
    SYSTEM_TTS_AVAILABLE = True
except ImportError:
    SYSTEM_TTS_AVAILABLE = False
    print("💡 Install pyttsx3 for voice: pip install pyttsx3")

# Try to import Google Cloud TTS for better voices
try:
    from google.cloud import texttospeech
    import pygame
    import tempfile
    GOOGLE_TTS_AVAILABLE = True
    print("✅ Google Cloud TTS available")
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    print("💡 Install google-cloud-texttospeech and pygame for better voice: pip install google-cloud-texttospeech pygame")

# Load environment variables
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Configure voice options
VOICE_READY = False

# Try ElevenLabs first (if available and has API key)
if ELEVENLABS_AVAILABLE:
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    if elevenlabs_key:
        try:
            set_api_key(elevenlabs_key)
            VOICE_READY = True
            VOICE_METHOD = "elevenlabs"
            print("✅ ElevenLabs configured")
        except Exception as e:
            print(f"⚠️ ElevenLabs setup failed: {e}")
    else:
        print("ℹ️ No ElevenLabs API key - trying alternatives...")

# Try Google Cloud TTS for authentic David Attenborough voice
if not VOICE_READY and GOOGLE_TTS_AVAILABLE:
    try:
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            tts_client = texttospeech.TextToSpeechClient()
            pygame.mixer.init()
            VOICE_READY = True
            VOICE_METHOD = "google_tts"
            print("✅ Google Cloud TTS configured with authentic David Attenborough voice")
        else:
            print("⚠️ Google Cloud TTS credentials not found")
    except Exception as e:
        print(f"⚠️ Google Cloud TTS setup failed: {e}")

# Try system TTS as fallback (with enhanced settings)
if not VOICE_READY and SYSTEM_TTS_AVAILABLE:
    try:
        tts_engine = pyttsx3.init()
        # Enhanced settings for dynamic, engaging David Attenborough-like voice
        tts_engine.setProperty('rate', 170)  # Faster, more engaging pace
        tts_engine.setProperty('volume', 1.0)  # Full volume for presence
        
        # Try to find the best available voice (prefer male, British, or engaging voices)
        voices_list = tts_engine.getProperty('voices')
        best_voice = None
        
        # Priority order: British > Engaging Male > Any Male > Default
        for voice in voices_list:
            voice_name = voice.name.lower()
            if any(word in voice_name for word in ['british', 'uk', 'gb', 'english']):
                best_voice = voice
                break
        
        if not best_voice:  # If no British voice, look for engaging male voices
            for voice in voices_list:
                voice_name = voice.name.lower()
                if any(word in voice_name for word in ['male', 'man', 'daniel', 'alex', 'david', 'tom', 'james']):
                    best_voice = voice
                    break
        
        if best_voice:
            tts_engine.setProperty('voice', best_voice.id)
            print(f"🎭 Using dynamic voice: {best_voice.name}")
        
        VOICE_READY = True
        VOICE_METHOD = "system_tts"
        print("✅ Enhanced System TTS configured for dynamic documentary narration")
    except Exception as e:
        print(f"⚠️ System TTS setup failed: {e}")

if not VOICE_READY:
    VOICE_METHOD = "text_only"
    print("📝 Running in text-only mode")

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    """Play audio using available voice method"""
    if not VOICE_READY:
        print("🔊 Text only (no voice available)")
        return
        
    try:
        if VOICE_METHOD == "elevenlabs":
            print("🎙️ Sir David speaking with ElevenLabs...")
            audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

            unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
            dir_path = os.path.join("narration", unique_id)
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "audio.wav")

            with open(file_path, "wb") as f:
                f.write(audio)

            play(audio)
            
        elif VOICE_METHOD == "google_tts":
            print("🎙️ Sir David preparing his dynamic documentary narration...")
            
            # Enhanced SSML for David Attenborough's engaging, varied style
            enhanced_text = f"""
            <speak>
                <prosody rate="medium" pitch="+1st" volume="loud">
                    <emphasis level="strong">{text}</emphasis>
                </prosody>
                <break time="0.2s"/>
            </speak>
            """
            
            # Create TTS request with SSML for better control
            synthesis_input = texttospeech.SynthesisInput(ssml=enhanced_text.strip())
            
            # Configure dynamic David Attenborough voice - more engaging!
            voice_options = [
                "en-GB-Neural2-D",   # Neural British male - most dynamic
                "en-GB-Wavenet-D",   # Premium British male voice  
                "en-GB-Standard-D",  # Standard British male voice
                "en-GB-Journey-D"    # Fallback
            ]
            
            response = None
            for voice_option in voice_options:
                try:
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="en-GB",
                        name=voice_option,
                        ssml_gender=texttospeech.SsmlVoiceGender.MALE
                    )
                    
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=1.1,   # Faster, more engaging pace
                        pitch=-1.0,          # Slightly deeper but not boring
                        volume_gain_db=4.0,  # Strong, confident presence
                        effects_profile_id=["headphone-class-device"]  # Clear, crisp sound
                    )
                    
                    response = tts_client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice,
                        audio_config=audio_config
                    )
                    
                    print(f"🎭 Using dynamic David voice: {voice_option}")
                    break
                    
                except Exception as voice_error:
                    print(f"⚠️ Voice {voice_option} failed: {voice_error}")
                    continue
            
            if not response:
                print("❌ All British voices failed")
                return
            
            # Save and play audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.write(response.audio_content)
            temp_file.close()
            
            print("🔊 Sir David speaking with dynamic documentary excitement!")
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            os.unlink(temp_file.name)
            
        elif VOICE_METHOD == "system_tts":
            print("🎙️ Sir David speaking with enhanced dynamic system voice...")
            
            # Make the voice more dynamic - faster and with varied emphasis
            tts_engine.setProperty('rate', 180)  # Faster, more engaging
            tts_engine.setProperty('volume', 1.0)  # Full volume for presence
            
            # Add dynamic emphasis and varied pacing like David Attenborough
            enhanced_text = text.replace('!', ' EXCITED!')
            enhanced_text = enhanced_text.replace('fascinating', 'FASCINATING')
            enhanced_text = enhanced_text.replace('remarkable', 'REMARKABLE')
            enhanced_text = enhanced_text.replace('extraordinary', 'EXTRAORDINARY')
            
            tts_engine.say(enhanced_text)
            tts_engine.runAndWait()
            
    except Exception as e:
        print(f"🔊 Audio failed: {e}")
        print("💬 (Text only)")


def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    # Build sophisticated context from conversation history
    narrative_context = ""
    observation_themes = set()  # Track themes to avoid repetition
    
    if len(script) > 0:
        recent_observations = script[-5:]  # More context for better continuity
        narrative_context = "\n\nOngoing Documentary Context:\n"
        
        # Build narrative progression
        if len(script) == 1:
            narrative_context += "This is our second observation - build upon the initial encounter.\n"
        elif len(script) < 5:
            narrative_context += f"We are {len(script) + 1} observations into this fascinating study.\n"
        else:
            narrative_context += f"After {len(script)} detailed observations, continue the evolving story.\n"
        
        # Extract themes to avoid repetition
        for i, obs in enumerate(recent_observations, 1):
            content = obs['content'].lower()
            narrative_context += f"Previous: {obs['content'][:100]}...\n"
            
            # Track common themes to avoid
            if 'hair' in content: observation_themes.add('hair')
            if 'glasses' in content or 'eyewear' in content: observation_themes.add('eyewear') 
            if 'clothing' in content or 'shirt' in content: observation_themes.add('clothing')
            if 'posture' in content or 'sitting' in content: observation_themes.add('posture')
            if 'screen' in content or 'computer' in content: observation_themes.add('technology')
    
    # Create enhanced David Attenborough system prompt with narrative progression
    system_prompt = f"""
    You are Sir David Attenborough providing continuous documentary narration. This is part of an ONGOING story - build upon previous observations while discovering NEW details.

    NARRATIVE GUIDELINES:
    - Reference the progression of time and behavioral changes 
    - Notice NEW details not mentioned before: expressions, micro-movements, environmental changes
    - Build character development - show how the subject evolves across observations
    - Use transitional phrases like "Meanwhile...", "As our observation continues...", "Now we witness..."
    - Make connections between past and present behavior patterns
    - Be delightfully surprised by unexpected changes or developments

    AVOID REPEATING these already-covered themes: {', '.join(observation_themes) if observation_themes else 'none yet'}
    
    {narrative_context}
    
    Focus on FRESH observations: new expressions, subtle movements, environmental changes, behavioral evolution, or anything that's different from previous observations. Build the story forward!
    """
    
    # Create the prompt for Gemini
    prompt_text = system_prompt + "\n\nNow analyze this image and provide your Sir David Attenborough narration:"
    
    # Use Gemini instead of OpenAI
    response = gemini_model.generate_content([
        prompt_text,
        {"mime_type": "image/jpeg", "data": base64_image}
    ])
    
    if response and response.text:
        response_text = response.text.strip()
        return response_text
    else:
        return "Fascinating... it appears our subject has rendered me speechless - a rare occurrence indeed!"


def main():
    print("🎬 David Attenborough AI Narrator")
    print("📝 Using Google Gemini for analysis")
    print(f"🔊 Voice method: {VOICE_METHOD}")
    print()
    
    # Load conversation history if it exists
    conversation_file = "david_attenborough_commentary.json"
    script = []
    
    try:
        if os.path.exists(conversation_file):
            with open(conversation_file, 'r') as f:
                script = json.load(f)
            print(f"📖 Loaded {len(script)} previous observations for narrative continuity")
    except Exception as e:
        print(f"⚠️ Could not load conversation history: {e}")
    
    frame_count = 0

    while True:
        # path to your image
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # getting the base64 encoding
        base64_image = encode_image(image_path)

        # analyze posture
        print("👀 David is watching...")
        analysis = analyze_image(base64_image, script=script)

        print("🎙️ David says:")
        print(analysis)

        play_audio(analysis)

        # Add to script with timestamp for better context
        script.append({
            "role": "assistant", 
            "content": analysis,
            "timestamp": time.time(),
            "frame": frame_count
        })
        
        frame_count += 1

        # Auto-save conversation history every 5 frames
        if frame_count % 5 == 0:
            try:
                with open(conversation_file, 'w') as f:
                    json.dump(script, f, indent=2)
                print(f"💾 Auto-saved conversation history ({len(script)} observations)")
            except Exception as e:
                print(f"⚠️ Could not save conversation: {e}")

        # wait for 5 seconds
        time.sleep(5)


if __name__ == "__main__":
    main()
