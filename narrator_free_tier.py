import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import texttospeech
import base64
import time
import simpleaudio as sa
import errno
from PIL import Image
import io
import asyncio
import simpleaudio as sa


# Load environment variables from .env file
load_dotenv()

# Set up Google Cloud credentials  
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keen-diode-417213-aca26ece4428.json'

# Configure Google AI - Free Tier Gemini Flash
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Google Cloud Text-to-Speech client with proper error handling
try:
    tts_client = texttospeech.TextToSpeechClient()
    TTS_AVAILABLE = True
    print("✅ Google Cloud TTS initialized successfully")
except Exception as e:
    TTS_AVAILABLE = False
    print(f"⚠️ Google Cloud TTS not available: {e}")
    print("📝 Will use text-only output")

def encode_image(image_path):
    """Encode image to base64 with retry logic for file locks"""
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                raise
            time.sleep(0.1)

def play_audio(text):
    """Generate and play David Attenborough style audio using Google Cloud TTS"""
    if not TTS_AVAILABLE:
        print(f"🎙️ David would say: {text}")
        return
        
    try:
        # Truncate text if too long to avoid TTS issues
        if len(text) > 500:
            text = text[:500] + "..."
            
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request - using a British voice for David Attenborough style
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Neural2-B",  # British male neural voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )

        # Select the type of audio file and voice settings for documentary style
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.85,  # Slightly slower for dramatic documentary effect
            pitch=-3.0,  # Lower pitch for David Attenborough gravitas
        )

        # Perform the text-to-speech request using Google Cloud
        response = tts_client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )

        # Save the audio file
        unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
        dir_path = os.path.join("narration", unique_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "audio.wav")

        # Write the response to the output file
        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        
        print(f"🎵 Audio saved to: {file_path}")

        # Try to play the audio file using simpleaudio (avoid segfault)
        try:
            print("🔊 Attempting to play audio...")
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            print("✅ Audio played successfully")
        except ImportError:
            print(f"📁 Audio file saved (simpleaudio not available for playback)")
            print(f"🎵 You can play: {file_path}")
        except Exception as play_error:
            print(f"⚠️ Audio playback issue: {play_error}")
            print(f"📁 Audio saved to: {file_path}")
            print(f"🎵 Try playing manually or use a different audio system")
            
    except Exception as e:
        print(f"⚠️ TTS error: {e}")
        print(f"📝 David would say: {text[:200]}...")

def analyze_image_free_tier(base64_image, script):
    """Free tier optimized Gemini Flash analysis with conversational David Attenborough style"""
    # Convert base64 to PIL Image for Gemini
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    
    # Build minimal conversation history to save tokens
    session_count = len(script) + 1
    
    # Very compact context to save API calls
    context = ""
    if script and len(script) > 0:
        context = f"Last observation: {script[-1]['content'][:100]}...\n"
    
    # Create efficient conversational prompt for free tier
    if session_count == 1:
        prompt = f"""You're David Attenborough casually observing a person. Talk naturally with contractions and British charm. Keep it concise but fascinating.

Style: Use "don't", "can't", "that's". Add "well," "you know," "quite". Include pauses with "...".

Notice key things: facial expressions, posture, clothing, lighting, unique details.

Be genuinely curious: "Well now, there's something quite interesting about..."
"""
    else:
        prompt = f"""Continue observing this person (session {session_count}). Find something new you didn't mention before.

{context}

Keep that conversational David style - natural, curious, British. What's different now?"""

    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return f"Well, I'm afraid I'm having a spot of trouble with my observations at the moment... the technical equipment needs a rest, you see. But I can tell there's definitely a fascinating specimen of Homo sapiens in view!"
        else:
            return f"Hmm, seems my observation equipment is having a technical difficulty... {error_msg[:50]}... But what a remarkable subject we have here!"

def main():
    """Free tier optimized main function"""
    script = []
    session_count = 0
    
    print("🎬 FREE TIER David Attenborough AI Narrator")
    print("💬 Conversational style with natural speech patterns!")
    print("🆓 Optimized for Gemini Flash free tier limits")
    print("⏰ 20-second intervals to respect quotas")
    print("📹 Make sure your webcam is capturing to frames/frame.jpg")
    print("🎙️ Google Cloud TTS (if available)")
    print("-" * 60)
    print("🔄 Free tier limits: ~15 requests/minute, 1500/day")
    print("💡 This version uses minimal tokens and smart timing")
    print("-" * 60)

    while True:
        try:
            # Path to your image
            image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")
            
            # Check if image exists
            if not os.path.exists(image_path):
                print("❌ No image found at frames/frame.jpg")
                print("💡 Run capture.py first to capture frames!")
                time.sleep(10)
                continue

            # Get the base64 encoding
            base64_image = encode_image(image_path)

            # Analyze with free tier optimization
            print("👀 David is observing (free tier mode)...")
            session_count += 1
            
            # Simple, efficient analysis
            analysis = analyze_image_free_tier(base64_image, script=script)

            print(f"💬 David's observation #{session_count}:")
            print("-" * 50)
            print(analysis)
            print("-" * 50)

            # Generate and play audio if available
            play_audio(analysis)

            # Update conversation history - keep minimal for efficiency
            script.append({"role": "assistant", "content": analysis})
            
            # Keep only last 2 observations to save tokens
            if len(script) > 2:
                script = script[-2:]

            # Conservative wait time for free tier
            print(f"⏳ Waiting 20 seconds to respect free tier limits (15 req/min)...")
            print(f"📊 Session {session_count} complete - staying within quotas")
            time.sleep(20)
            
        except KeyboardInterrupt:
            print("\n🎬 David ended his observation session. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Waiting 30 seconds before retry...")
            time.sleep(30)

if __name__ == "__main__":
    print("🎬 FREE TIER David Attenborough AI Narrator")
    print("🆓 Gemini Flash Optimized | Conservative API Usage")
    print("💬 Full Conversational Style Within Free Limits")
    print("=" * 60)
    main()
