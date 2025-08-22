import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import texttospeech
import base64
import json
import time
import simpleaudio as sa
import errno
from elevenlabs import generate, play, set_api_key, voices
from PIL import Image
import io
from portia import Portia, Config, StorageClass, LogLevel
from portia import PlanBuilderV2, StepOutput, Input, Portia
from portia.open_source_tools.registry import example_tool_registry
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio

# Load environment variables from .env file
load_dotenv()

# Pydantic models for structured Portia outputs
class ImageAnalysis(BaseModel):
    """Structured output for detailed image analysis"""
    facial_expression: str = Field(description="Detailed description of facial expressions and micro-expressions")
    body_posture: str = Field(description="Exact body positioning, posture, and stance") 
    clothing_details: str = Field(description="Detailed clothing analysis including textures, colors, fit")
    environmental_context: str = Field(description="Background, lighting, and environmental details")
    unique_characteristics: str = Field(description="Any distinctive features, objects, or accessories")
    scientific_observations: str = Field(description="Detailed behavioral and physical observations")

class AttenboroughNarration(BaseModel):
    """Structured output for David Attenborough style narration"""
    narration: str = Field(description="Complete David Attenborough documentary narration")
    dramatic_elements: List[str] = Field(description="Key dramatic moments and build-ups")
    scientific_terminology: List[str] = Field(description="Scientific terms and concepts used")
    signature_phrases: List[str] = Field(description="Signature David Attenborough phrases used")

class ContinuousNarration(BaseModel):
    """Structured output for enhanced continuous documentary commentary"""
    enhanced_narration: str = Field(description="Enhanced continuous documentary narration")
    continuity_elements: List[str] = Field(description="Elements connecting to previous observations")  
    micro_details: List[str] = Field(description="Additional micro-details highlighted")
    anticipation_building: str = Field(description="Elements that build anticipation for future observations")

# Set up Google Cloud credentials  
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keen-diode-417213-aca26ece4428.json'

# Initialize Portia configuration
my_config = Config.from_default(
    storage_class=StorageClass.DISK, 
    storage_dir='demo_runs',
    default_log_level=LogLevel.DEBUG,
    llm_redis_cache_url="redis://localhost:6379"
)

# Initialize Portia for AI orchestration
portia_client = Portia(
    config=my_config,
    tools=example_tool_registry
)

# Configure Google AI for vision analysis with Gemini Pro
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')  # Using Pro version for better performance and higher limits

# Initialize Google Cloud Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

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

    # Play the audio file using simpleaudio
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        print(f"Could not play audio: {e}")
        print("Audio saved to:", file_path)

def create_attenborough_plan():
    """Create sophisticated Portia plan for David Attenborough narration"""
    plan = (
        PlanBuilderV2()
        .input(
            name="image_data", 
            description="Base64 encoded image of the human subject to analyze"
        )
        .input(
            name="previous_context", 
            description="Previous narration context to avoid repetition",
            default_value=""
        )
        .input(
            name="session_count",
            description="Number of previous observation sessions",
            default_value=1
        )
        
        # Step 1: Detailed Visual Analysis with conversational style (Enhanced with Gemini Pro)
        .llm_step(
            task="""You are Sir David Attenborough's research assistant, but keep it conversational. With Gemini Pro's enhanced capabilities, analyze this image of a human with incredibly detailed observations, but talk naturally - not overly formal.

Focus on micro-details that only advanced AI can catch:
- Facial expressions and micro-expressions - what's their face doing? Tiny muscle movements?
- Body positioning and posture - how are they sitting/positioned? Weight distribution?
- Clothing details - textures, colors, fit, style, fabric behavior, wrinkles
- Environmental context - lighting quality, shadows, background elements, reflections
- Any unique characteristics or objects - jewelry, accessories, personal items
- Physiological details - skin texture, hair patterns, breathing patterns
- Tiny details most people would miss - micro-gestures, eye movements, subtle asymmetries

With Pro's enhanced vision, notice everything but talk like you're sharing fascinating observations with a friend. Use contractions and natural language while being thorough and scientific.

Image data: {{image_data}}
Previous context: {{previous_context}}""",
            inputs=["image_data", "previous_context"],
            step_name="visual_analysis"
        )
        
        # Step 2: David Attenborough Conversational Narration  
        .llm_step(
            task="""You are Sir David Attenborough, but you're just casually chatting about this person you're watching. Don't go full documentary mode - talk naturally like you're sharing observations with a friend over tea.

YOUR CONVERSATIONAL STYLE:
- Use contractions like "don't", "can't", "that's", "I'm"
- Throw in natural words like "well," "you know," "so," "I mean" (but don't overdo it)
- Add natural pauses with "..." or "--" 
- Mix short observations with longer thoughts
- Sound genuinely curious, not rehearsed
- Keep that gentle British curiosity, but more relaxed
- Still call them "Homo sapiens" because... well, that's just how you think

Based on this analysis: {{visual_analysis}}
Previous context: {{previous_context}}
Session number: {{session_count}}

Just be fascinated by this person's behavior and share what catches your eye naturally.""",
            inputs=[StepOutput("visual_analysis"), "previous_context", "session_count"],
            step_name="attenborough_narration"
        )
        
        # Step 3: Enhanced Continuous Commentary
        .llm_step(
            task="""Take David's conversational narration and enhance it while keeping that natural, human-like speaking style. Make it more detailed and continuous but don't lose the conversational feel.

Add more:
- Micro-details and observations
- Natural connections to previous sessions
- Anticipation for what might happen next
- That signature David fascination with tiny details
- Natural speech patterns and flow

Keep it feeling like a casual but detailed chat about human behavior.

Original narration: {{attenborough_narration}}""",
            inputs=[StepOutput("attenborough_narration")],
            step_name="continuous_enhancement"
        )
        
        .final_output(StepOutput("continuous_enhancement"))
        .build()
    )
    
    return plan

async def analyze_image_with_portia(base64_image, script):
    """Analyze image using sophisticated Portia PlanBuilderV2 with conversational style"""
    try:
        # Create the sophisticated plan
        plan = create_attenborough_plan()
        
        # Prepare context from previous observations
        previous_context = ""
        session_count = len(script) + 1
        
        for i, msg in enumerate(script[-3:], 1):  # Last 3 observations for context
            if msg["role"] == "assistant":
                previous_context += f"Previous chat {i}: {msg['content']}\n\n"
        
        print("🤖 Executing sophisticated Portia plan for conversational David Attenborough narration...")
        
        # Execute the plan using the correct Portia method
        try:
            result = await portia_client.run_async(
                plan_definition=plan,
                inputs={
                    "image_data": base64_image,
                    "previous_context": previous_context,
                    "session_count": session_count
                }
            )
            
            if result and hasattr(result, 'output'):
                enhanced_narration = result.output.strip()
                print("✅ Portia plan execution successful!")
                return enhanced_narration
            elif result:
                # Handle different result formats
                narration = str(result).strip()
                if narration and len(narration) > 50:
                    print("✅ Portia plan execution successful!")
                    return narration
                    
        except Exception as portia_exec_error:
            print(f"⚠️ Portia execution error: {portia_exec_error}")
        
        # Fallback to enhanced Gemini if plan doesn't work
        print("🔄 Falling back to enhanced Gemini analysis")
        return analyze_image_with_enhanced_gemini(base64_image, script)
            
    except Exception as e:
        print(f"❌ Portia plan error: {e}")
        print("🔄 Falling back to enhanced Gemini analysis")
        return analyze_image_with_enhanced_gemini(base64_image, script)

def analyze_image_with_enhanced_gemini(base64_image, script):
    """Enhanced Gemini Pro analysis with conversational David Attenborough style"""
    # Convert base64 to PIL Image for Gemini Pro
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    
    # Build conversation history
    conversation_history = ""
    session_count = len(script) + 1
    
    for i, msg in enumerate(script[-3:], 1):  # Keep recent context
        if msg["role"] == "assistant":
            conversation_history += f"Previous chat {i}: {msg['content']}\n\n"
    
    # Create conversational prompt optimized for Gemini Pro
    if session_count == 1:
        detailed_prompt = """You're Sir David Attenborough, but you're just casually starting to observe this person. With Gemini Pro's enhanced vision capabilities, you can see incredible detail - but don't go full documentary mode. Just talk naturally like you're sharing observations with a friend over tea.

YOUR CONVERSATIONAL STYLE:
- Use contractions like "don't", "can't", "that's", "I'm" instead of formal speech
- Throw in natural words like "well," "you know," "so," "I mean" (but don't overdo it)
- Add natural pauses with "..." or "--" like real conversation
- Mix short observations with longer thoughts
- Sound genuinely curious, not rehearsed
- Keep that gentle British curiosity, but more relaxed
- Still call them "Homo sapiens" because... well, that's just how you think

With Pro's enhanced vision, notice EVERYTHING, but talk about it naturally:
- Micro-expressions - tiny muscle movements around eyes, mouth, forehead
- Subtle body language - weight shifts, hand positions, finger movements
- Clothing and fabric behavior - how materials fall, wrinkles, textures
- Environmental details - lighting quality, reflections, shadows, background elements
- Physiological observations - breathing patterns, skin texture, hair details
- Tiny behavioral cues - eye movements, micro-gestures, asymmetries
- Object interactions - how they relate to items around them

Just be fascinated by this person's behavior. Talk about what catches your eye with that enhanced detail Pro provides.

Make it feel like: "So I've been watching this person and... you know what's interesting? The way they..."
"""
    else:
        detailed_prompt = f"""You're Sir David Attenborough continuing to chat about this person you've been watching. This is conversation #{session_count}. With Gemini Pro's superior vision, you can see details others miss - don't repeat what you said before, find something new to talk about.

WHAT YOU'VE SAID BEFORE:
{conversation_history}

Keep that conversational style - contractions, natural pauses, casual observations. Connect to what you said before but always find fresh micro-details to geek out about. With Pro's enhanced capabilities, you can spot:
- New micro-expressions and facial changes
- Subtle posture adjustments and body language shifts
- Different lighting angles revealing new details
- Clothing texture changes or fabric behavior
- Environmental elements you missed before
- Physiological details like breathing or skin texture changes
- Tiny behavioral patterns and micro-movements

Talk like you're genuinely curious about human behavior and Pro is showing you fascinating new details.
"""

    response = model.generate_content([detailed_prompt, image])
    return response.text

async def main():
    """Enhanced main function with Portia integration and conversational style"""
    script = []
    session_count = 0
    
    print("🎬 Conversational David Attenborough AI Narrator with Portia!")
    print("💬 Now with human-like speaking patterns!")
    print("� Enhanced with Gemini Pro for superior vision analysis!")
    print("�📹 Make sure your webcam is capturing to frames/frame.jpg")
    print("🎙️ Using Google Cloud TTS with British voice")
    print("🤖 Powered by Portia AI orchestration")
    print("-" * 60)

    while True:
        try:
            # Path to your image
            image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")
            
            # Check if image exists
            if not os.path.exists(image_path):
                print("❌ No image found at frames/frame.jpg")
                print("💡 Make sure to run capture.py first to capture frames!")
                time.sleep(5)
                continue

            # Get the base64 encoding
            base64_image = encode_image(image_path)

            # Analyze with enhanced Portia integration
            print("👀 David is casually observing...")
            session_count += 1
            
            # Use sophisticated Portia analysis with conversational style
            analysis = await analyze_image_with_portia(base64_image, script=script)

            print(f"💬 David chats (Session {session_count}):")
            print("-" * 50)
            print(analysis)
            print("-" * 50)

            # Generate and play audio
            play_audio(analysis)

            # Update conversation history - keep recent observations for continuity
            script.append({"role": "assistant", "content": analysis})
            
            # Keep recent history for better conversational context
            if len(script) > 8:
                script = script[-8:]

            # Wait before next observation
            print(f"⏳ Waiting 4 seconds before next casual observation...")
            time.sleep(4)
            
        except KeyboardInterrupt:
            print("\n🎬 Conversational David ended the chat. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            print("🔄 Continuing with next observation...")
            time.sleep(2)

def run_narrator():
    """Wrapper function to run the async main"""
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to run narrator: {e}")
        print("Falling back to basic mode...")

if __name__ == "__main__":
    print("🎬 Conversational David Attenborough AI Narrator")
    print("💬 Enhanced with Human-like Speaking Patterns + Portia AI")
    print("=" * 60)
    run_narrator()
