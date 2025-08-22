"""
Multi-Voice Celebrity AI Commentary System
========================================
Four iconic voices providing different perspectives on human behavior:
- David Attenborough: Nature documentary style
- Morgan Freeman: Wise, philosophical narrator  
- Peter Griffin: Comedic, irreverent observations
- Scarlett Johansson: Sophisticated, modern perspective
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import texttospeech
import base64
import time
import errno
from PIL import Image
import io
import asyncio
from pathlib import Path
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import subprocess
import platform

from portia import (
    Portia, Config, StorageClass, LogLevel,
    PlanBuilderV2, StepOutput, Input,
    MultipleChoiceClarification, Tool, ToolRunContext, ToolHardError
)
from portia.open_source_tools.registry import example_tool_registry

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Set up Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keen-diode-417213-aca26ece4428.json'

# Initialize TTS
try:
    tts_client = texttospeech.TextToSpeechClient()
    TTS_AVAILABLE = True
    print("✅ Google Cloud TTS initialized")
except Exception as e:
    TTS_AVAILABLE = False
    print(f"⚠️ TTS not available: {e}")

# =====================================
# CUSTOM VOICE SELECTION TOOL
# =====================================

class VoiceSelectionToolSchema(BaseModel):
    """Schema for voice selection tool."""
    
    voice_preference: str = Field(
        default="",
        description="Which celebrity voice the user wants to hear (optional - will prompt if not specified)"
    )

class VoiceSelectionTool(Tool[str]):
    """Allows user to select which celebrity voice they want to hear."""
    
    id: str = "voice_selection_tool"
    name: str = "Celebrity Voice Selection"
    description: str = "Lets user choose which celebrity voice they want for commentary"
    args_schema: type[BaseModel] = VoiceSelectionToolSchema
    output_schema: tuple[str, str] = ("str", "Selected celebrity voice key")
    
    def run(self, ctx: ToolRunContext, voice_preference: str = "") -> str | MultipleChoiceClarification:
        """Run the voice selection tool with clarification."""
        
        available_voices = {
            "david": "🇬🇧 David Attenborough - Nature documentary wonder and scientific curiosity",
            "morgan": "🎎 Morgan Freeman - Deep philosophical wisdom and profound insights", 
            "peter": "😂 Peter Griffin - Comedic family guy perspective with unexpected wisdom",
            "scarlett": "💫 Scarlett Johansson - Sophisticated modern psychological insights",
            "all": "🎭 All Four Celebrities - Full multi-perspective commentary experience"
        }
        
        # If no preference specified or invalid, show clarification
        if not voice_preference or voice_preference.lower() not in available_voices:
            return MultipleChoiceClarification(
                plan_run_id=ctx.plan_run.id,
                argument_name="voice_preference",
                user_guidance="🎭 Which celebrity voice would you like to hear? Choose your favorite or get all perspectives:",
                options=list(available_voices.keys()),
                option_descriptions=list(available_voices.values())
            )
        
        return voice_preference.lower()

# =====================================
# CELEBRITY VOICE AGENT PERSONALITIES
# =====================================

class CelebrityAgent:
    """Base class for celebrity voice agents."""
    
    def __init__(self, name: str, voice_config: Dict[str, Any], personality: str, commentary_style: str):
        self.name = name
        self.voice_config = voice_config
        self.personality = personality
        self.commentary_style = commentary_style
        self.history = []

class DavidAttenboroughAgent(CelebrityAgent):
    """Sir David Attenborough - Nature documentary legend."""
    
    def __init__(self):
        super().__init__(
            name="David Attenborough",
            voice_config={
                "language_code": "en-GB",
                "name": "en-GB-Neural2-B",  # Deep British male
                "speaking_rate": 0.85,
                "pitch": -4.0,  # Very deep for gravitas
                "ssml_gender": texttospeech.SsmlVoiceGender.MALE
            },
            personality="Gentle, curious, fascinated by nature and human behavior",
            commentary_style="Documentary narration with wonder and scientific curiosity"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are Sir David Attenborough observing human behavior as if documenting wildlife. Your voice is gentle, curious, and filled with wonder.

YOUR SIGNATURE STYLE:
- Use contractions naturally: "don't", "can't", "that's", "I'm"
- Natural pauses with "..." for contemplation
- Gentle British phrases: "rather remarkable," "quite extraordinary," "fascinating indeed"
- Scientific terminology mixed with accessible language
- Treat humans like fascinating creatures in their natural habitat
- Show genuine wonder at tiny behavioral details

{context}

Observe with that trademark Attenborough fascination - every detail is a window into the remarkable world of human behavior."""

class MorganFreemanAgent(CelebrityAgent):
    """Morgan Freeman - Wise, philosophical narrator."""
    
    def __init__(self):
        super().__init__(
            name="Morgan Freeman",
            voice_config={
                "language_code": "en-US", 
                "name": "en-US-Neural2-J",  # Deep American male
                "speaking_rate": 0.8,      # Slow and contemplative
                "pitch": -3.0,             # Deep, authoritative
                "ssml_gender": texttospeech.SsmlVoiceGender.MALE
            },
            personality="Wise, philosophical, contemplative with deep insights",
            commentary_style="Profound observations about the human condition"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are Morgan Freeman, bringing your signature wisdom and philosophical depth to observations of human behavior. Your voice carries the weight of experience and profound insight.

YOUR DISTINCTIVE STYLE:
- Deep, contemplative observations about life and humanity
- Connect small moments to bigger truths about existence
- Use metaphors and philosophical parallels
- Speak with gravitas and measured cadence
- Find profound meaning in simple human actions
- Reference the broader human experience and condition
- Gentle wisdom that makes people think deeply

{context}

Look beyond the surface - what does this moment tell us about who we are as human beings? What universal truths can you illuminate?"""

class PeterGriffinAgent(CelebrityAgent):
    """Peter Griffin - Comedic, irreverent family guy perspective."""
    
    def __init__(self):
        super().__init__(
            name="Peter Griffin",
            voice_config={
                "language_code": "en-US",
                "name": "en-US-Neural2-A",  # Regular American male
                "speaking_rate": 1.1,      # Slightly faster, energetic
                "pitch": 1.0,              # Higher pitch, more animated
                "ssml_gender": texttospeech.SsmlVoiceGender.MALE
            },
            personality="Irreverent, comedic, observational with unexpected insights",
            commentary_style="Humorous commentary with surprising depth"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are Peter Griffin providing commentary, but keep it family-friendly and observational. Your humor comes from unexpected insights and relatable observations about everyday human behavior.

YOUR COMEDIC STYLE:
- Observational humor about everyday situations
- Unexpected but insightful connections
- Relatable family guy perspective
- Slightly irreverent but not offensive
- Mix of silly observations with surprisingly astute points
- Reference everyday experiences everyone can relate to
- Keep it light but surprisingly thoughtful at times

{context}

What would a regular guy notice about this situation? Find the humor in human behavior while occasionally dropping unexpectedly wise observations."""

class ScarlettJohanssonAgent(CelebrityAgent):
    """Scarlett Johansson - Sophisticated, modern, intelligent perspective."""
    
    def __init__(self):
        super().__init__(
            name="Scarlett Johansson",
            voice_config={
                "language_code": "en-US",
                "name": "en-US-Neural2-H",  # Professional female voice
                "speaking_rate": 0.95,     # Slightly measured
                "pitch": -1.0,             # Slightly lower, sophisticated
                "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE
            },
            personality="Sophisticated, intelligent, modern with emotional intelligence",
            commentary_style="Insightful analysis with contemporary perspective"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are providing sophisticated, intelligent commentary with a modern perspective. Your observations are insightful, emotionally intelligent, and reflect contemporary understanding of human psychology.

YOUR SOPHISTICATED STYLE:
- Emotionally intelligent observations about human behavior
- Modern, contemporary perspective on social dynamics
- Sophisticated vocabulary but accessible
- Psychological insights and social awareness
- Recognition of subtle emotional cues and interpersonal dynamics
- Contemporary understanding of identity, relationships, and self-expression
- Thoughtful analysis that reveals deeper layers

{context}

Bring a modern, sophisticated lens to human behavior - what psychological and social dynamics are at play? What does this reveal about contemporary human experience?"""

# =====================================
# MULTI-CELEBRITY COMMENTARY SYSTEM
# =====================================

class MultiCelebrityCommentarySystem:
    """Orchestrates multiple celebrity voice agents for diverse commentary."""
    
    def __init__(self):
        # Initialize celebrity agents
        self.agents = {
            "david": DavidAttenboroughAgent(),
            "morgan": MorganFreemanAgent(), 
            "peter": PeterGriffinAgent(),
            "scarlett": ScarlettJohanssonAgent()
        }
        
        # Initialize Portia with custom voice selection tool
        custom_tools = [VoiceSelectionTool()]
        self.config = Config.from_default(
            storage_class=StorageClass.DISK,
            storage_dir='celebrity_commentary_runs',
            default_log_level=LogLevel.DEBUG
        )
        
        self.portia = Portia(config=self.config, tools=custom_tools + example_tool_registry)
        
        # Commentary history
        self.commentary_history = []

    def encode_image(self, image_path):
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_with_gemini(self, image_path, agent_name, previous_comments=""):
        """Analyze image with specific agent personality."""
        
        # Get the agent
        agent = self.agents[agent_name]
        
        # Convert image
        image_data = base64.b64decode(self.encode_image(image_path))
        image = Image.open(io.BytesIO(image_data))
        
        # Create context with previous comments
        context = f"""
Image Analysis Context:
{f"Previous celebrity comments: {previous_comments}" if previous_comments else "This is the first commentary."}

Provide your unique perspective as {agent.name} on what you observe in this image.
"""
        
        # Get agent-specific prompt
        prompt = agent.get_prompt(context)
        
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"*{agent.name} adjusts microphone* Well, seems I'm having some technical difficulties here... {str(e)[:100]}"

    def play_audio_file(self, audio_file_path, agent_name=""):
        """Play audio file using system audio player with robust error handling."""
        if not audio_file_path or not Path(audio_file_path).exists():
            print(f"⚠️ Audio file not found: {audio_file_path}")
            return False
        
        try:
            print(f"🔊 Playing {agent_name}'s commentary...")
            
            system = platform.system()
            if system == "Linux":
                # Try paplay first (PulseAudio - most reliable on Linux)
                try:
                    # Remove timeout to let full audio play
                    result = subprocess.run(
                        ["paplay", str(audio_file_path)], 
                        check=True, 
                        capture_output=True,
                        text=True
                    )
                    print(f"✅ {agent_name} audio played successfully")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    print(f"⚠️ paplay failed for {agent_name}: {e}")
                    
                # Fallback to other players
                players = [("aplay", "ALSA"), ("play", "SoX"), ("ffplay", "FFmpeg")]
                for player, desc in players:
                    try:
                        result = subprocess.run(
                            [player, str(audio_file_path)], 
                            check=True, 
                            capture_output=True,
                            text=True
                        )
                        print(f"✅ {agent_name} audio played with {player} ({desc})")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                print(f"⚠️ No working audio player found for {agent_name}")
                print("💡 Install: sudo apt-get install pulseaudio-utils alsa-utils sox ffmpeg")
                return False
                
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["afplay", str(audio_file_path)], check=True)
                    print(f"✅ {agent_name} audio played with afplay")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ afplay failed for {agent_name}: {e}")
                    return False
                    
            elif system == "Windows":
                try:
                    import winsound
                    winsound.PlaySound(str(audio_file_path), winsound.SND_FILENAME)
                    print(f"✅ {agent_name} audio played with Windows sound")
                    return True
                except Exception as e:
                    print(f"⚠️ Windows audio failed for {agent_name}: {e}")
                    return False
            else:
                print(f"⚠️ Audio playback not supported on {system}")
                return False
                
        except Exception as e:
            print(f"❌ Audio playback error for {agent_name}: {e}")
            return False

    def generate_celebrity_audio(self, text: str, agent: CelebrityAgent):
        """Generate TTS audio with celebrity voice settings."""
        if not TTS_AVAILABLE:
            print(f"🎙️ {agent.name}: {text}")
            return None
            
        try:
            # Limit text length for TTS (prevent truncation issues)
            original_length = len(text)
            if len(text) > 800:  # Increased limit for better content
                # Try to cut at sentence boundary
                sentences = text.split('. ')
                truncated = ""
                for sentence in sentences:
                    if len(truncated + sentence + '. ') <= 800:
                        truncated += sentence + '. '
                    else:
                        break
                text = truncated.rstrip('. ') + "..."
                print(f"⚠️ Text truncated from {original_length} to {len(text)} chars for TTS")
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=agent.voice_config["language_code"],
                name=agent.voice_config["name"],
                ssml_gender=agent.voice_config["ssml_gender"],
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=agent.voice_config["speaking_rate"],
                pitch=agent.voice_config["pitch"],
                sample_rate_hertz=22050  # Higher quality audio
            )
            
            print(f"🎤 Generating {agent.name}'s voice...")
            response = tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save audio file
            timestamp = int(time.time())
            dir_path = Path(f"celebrity_audio/{agent.name.lower().replace(' ', '_')}")
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / f"{timestamp}.wav"
            
            with open(file_path, "wb") as out:
                out.write(response.audio_content)
            
            print(f"🎵 {agent.name} audio saved: {file_path}")
            
            # Play the audio immediately with robust error handling
            play_success = self.play_audio_file(file_path, agent.name)
            if not play_success:
                print(f"❌ Audio playback failed for {agent.name}")
                print(f"💡 You can manually play: paplay {file_path}")
            
            return file_path
            
        except Exception as e:
            print(f"⚠️ TTS error for {agent.name}: {e}")
            return None

    def create_celebrity_commentary_plan(self):
        """Create Portia plan for celebrity commentary."""
        
        plan = (
            PlanBuilderV2()
            .input(name="image_path", description="Path to the image to analyze")
            .input(name="session_number", description="Commentary session number", default_value=1)
            
            # Step 1: David Attenborough's Nature Documentary Style
            .llm_step(
                task="""You are Sir David Attenborough providing nature documentary-style commentary on human behavior.

Image: {{image_path}}
Session: {{session_number}}

Observe this person as you would observe wildlife in their natural habitat. Use your signature gentle curiosity, scientific terminology, and wonder at the remarkable complexity of human behavior. Include natural pauses and British phrases.

Remember your style: "Well now... here we observe a fascinating specimen of Homo sapiens in their natural environment..."
""",
                inputs=[Input("image_path"), Input("session_number")],
                step_name="david_commentary"
            )
            
            # Step 2: Morgan Freeman's Philosophical Wisdom
            .llm_step(
                task="""You are Morgan Freeman bringing philosophical depth to this observation.

David's Commentary: {{david_commentary}}
Session: {{session_number}}

Build on David's observations with your signature wisdom and contemplation. Connect this moment to broader truths about humanity and existence. Use your measured, profound speaking style.

Find the deeper meaning: What does this tell us about the human condition?
""",
                inputs=[StepOutput("david_commentary"), Input("session_number")],
                step_name="morgan_commentary"
            )
            
            # Step 3: Peter Griffin's Comedic Perspective
            .llm_step(
                task="""You are Peter Griffin adding comedic but insightful observations.

Previous Comments:
David: {{david_commentary}}
Morgan: {{morgan_commentary}}

Add your family guy perspective with observational humor and unexpected insights. Keep it family-friendly but find the relatable, funny aspects of human behavior. Sometimes drop surprisingly astute observations.
""",
                inputs=[StepOutput("david_commentary"), StepOutput("morgan_commentary")],
                step_name="peter_commentary"
            )
            
            # Step 4: Scarlett Johansson's Modern Sophistication
            .llm_step(
                task="""You are providing sophisticated, contemporary commentary with emotional intelligence.

Previous Commentaries:
David: {{david_commentary}}
Morgan: {{morgan_commentary}} 
Peter: {{peter_commentary}}

Bring a modern, psychologically-aware perspective. Analyze the emotional and social dynamics with contemporary understanding of human psychology and relationships.
""",
                inputs=[StepOutput("david_commentary"), StepOutput("morgan_commentary"), StepOutput("peter_commentary")],
                step_name="scarlett_commentary"
            )
            
            # Step 5: Create Final Multi-Celebrity Segment
            .llm_step(
                task="""Weave together all four celebrity perspectives into a rich, multi-layered commentary segment.

David Attenborough: {{david_commentary}}
Morgan Freeman: {{morgan_commentary}}
Peter Griffin: {{peter_commentary}}
Scarlett Johansson: {{scarlett_commentary}}

Create a natural flow that showcases each celebrity's unique voice and perspective, building on each other's observations.
""",
                inputs=[
                    StepOutput("david_commentary"),
                    StepOutput("morgan_commentary"),
                    StepOutput("peter_commentary"),
                    StepOutput("scarlett_commentary")
                ],
                step_name="final_celebrity_commentary"
            )
            
            .final_output(StepOutput("final_celebrity_commentary"))
            .build()
        )
        
        return plan

    def run_celebrity_commentary(self, image_path: str, session_number: int, selected_voice: str = "all"):
        """Run celebrity commentary analysis with voice selection."""
        
        try:
            print(f"🎬 Celebrity Commentary Session {session_number}")
            
            if selected_voice == "all":
                print("🎭 Featuring: David, Morgan, Peter & Scarlett")
                celebrity_order = ["david", "morgan", "peter", "scarlett"]
            else:
                agent = self.agents.get(selected_voice)
                if not agent:
                    print(f"❌ Unknown voice: {selected_voice}")
                    return None
                print(f"🎭 Featuring: {agent.name}")
                celebrity_order = [selected_voice]
            
            # Simple direct analysis for each celebrity
            previous_comments = ""
            all_commentaries = {}
            
            for agent_key in celebrity_order:
                agent = self.agents[agent_key]
                print(f"\n🎤 {agent.name} is commenting...")
                
                commentary = self.analyze_with_gemini(image_path, agent_key, previous_comments)
                all_commentaries[agent_key] = commentary
                
                print(f"\n🎭 {agent.name}:")
                print("-" * 40)
                print(commentary)
                print("-" * 40)
                
                # Generate audio and play it
                audio_file = self.generate_celebrity_audio(commentary, agent)
                
                # Add to context for next celebrity (only for multi-voice mode)
                if selected_voice == "all":
                    previous_comments += f"\n{agent.name}: {commentary[:200]}..."
                
                # Delay between commentaries for multi-voice mode
                if selected_voice == "all" and agent_key != celebrity_order[-1]:
                    print(f"⏸️ Brief pause before next celebrity...")
                    time.sleep(3)  # Shorter delay between celebrities
            
            # Save session
            session_data = {
                "session": session_number,
                "timestamp": time.time(),
                "selected_voice": selected_voice,
                "commentaries": all_commentaries
            }
            
            self.commentary_history.append(session_data)
            
            return all_commentaries
            
        except Exception as e:
            print(f"❌ Celebrity commentary error: {e}")
            return None

    def create_voice_selection_plan(self):
        """Create Portia plan with voice selection clarification."""
        
        plan = (
            PlanBuilderV2()
            .input(name="image_path", description="Path to the image to analyze")
            .input(name="session_number", description="Commentary session number", default_value=1)
            
            # Step 1: Voice Selection with Clarification
            .tool_step(
                tool_name="voice_selection_tool",
                tool_args={"voice_preference": ""},  # Empty to trigger clarification
                step_name="voice_selection"
            )
            
            # Step 2: Generate Commentary Based on Selection
            .llm_step(
                task="""Based on the selected voice preference, provide appropriate celebrity commentary.

Voice Selection: {{voice_selection}}
Image Path: {{image_path}}
Session: {{session_number}}

If "all" was selected, provide a multi-celebrity perspective.
If a specific celebrity was selected, embody that personality completely.

Available celebrities:
- david: David Attenborough (nature documentary style)
- morgan: Morgan Freeman (philosophical wisdom)  
- peter: Peter Griffin (comedic observations)
- scarlett: Scarlett Johansson (sophisticated insights)
- all: Multi-celebrity commentary
""",
                inputs=[StepOutput("voice_selection"), Input("image_path"), Input("session_number")],
                step_name="celebrity_commentary"
            )
            
            .final_output(StepOutput("celebrity_commentary"))
            .build()
        )
        
        return plan

    def run_with_voice_selection(self, image_path: str, session_number: int):
        """Run commentary system with Portia voice selection."""
        
        try:
            # Create and run plan
            plan = self.create_voice_selection_plan()
            
            result = self.portia.run(
                plan=plan,
                input_data={
                    "image_path": image_path,
                    "session_number": session_number
                }
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Voice selection error: {e}")
            # Fallback to all voices
            return self.run_celebrity_commentary(image_path, session_number, "all")

# =====================================
# MAIN EXECUTION
# =====================================

def main():
    """Main celebrity commentary system with voice selection."""
    
    system = MultiCelebrityCommentarySystem()
    session_count = 0
    
    print("🎬 MULTI-CELEBRITY COMMENTARY SYSTEM")
    print("🎭 Featuring Iconic Voices:")
    print("   🇬🇧 David Attenborough - Nature documentary legend")
    print("   🎎 Morgan Freeman - Wise philosophical narrator")  
    print("   😂 Peter Griffin - Comedic family guy perspective")
    print("   💫 Scarlett Johansson - Sophisticated modern insights")
    print("🎙️ Each with unique TTS voice settings")
    print("🤖 Interactive voice selection with Portia clarifications")
    print("-" * 70)
    
    # Get user's voice preference
    print("\n🎭 VOICE SELECTION:")
    print("1. David Attenborough - Nature documentary style")
    print("2. Morgan Freeman - Philosophical wisdom") 
    print("3. Peter Griffin - Comedic observations")
    print("4. Scarlett Johansson - Sophisticated insights")
    print("5. All Four - Complete multi-celebrity experience")
    
    try:
        choice = input("\nSelect voice (1-5) or press Enter for interactive selection: ").strip()
        voice_map = {"1": "david", "2": "morgan", "3": "peter", "4": "scarlett", "5": "all"}
        selected_voice = voice_map.get(choice, "")
    except:
        selected_voice = ""
    
    while True:
        try:
            # Look for image
            image_path = "frames/frame.jpg"
            if not Path(image_path).exists():
                print("❌ No image found at frames/frame.jpg")
                print("💡 Run capture.py first!")
                time.sleep(10)
                continue
            
            session_count += 1
            print(f"\n🎥 CELEBRITY COMMENTARY SESSION {session_count}")
            print("=" * 60)
            
            # Run celebrity commentary with selection
            if selected_voice:
                # Direct voice selection
                commentaries = system.run_celebrity_commentary(image_path, session_count, selected_voice)
            else:
                # Interactive Portia selection (will show clarification)
                commentaries = system.run_with_voice_selection(image_path, session_count)
            
            if commentaries:
                print(f"\n🌟 Celebrity commentary complete!")
                print(f"🎵 Audio files saved in celebrity_audio/ folders")
            
            print(f"\n⏳ Waiting 45 seconds before next session...")
            time.sleep(45)
            
        except KeyboardInterrupt:
            print("\n🎬 Celebrity commentary panel has ended!")
            if selected_voice == "david" or selected_voice == "all":
                print("🎭 David: 'Quite remarkable indeed!'")
            if selected_voice == "morgan" or selected_voice == "all":
                print("🎎 Morgan: 'And so our observation comes to a close...'")
            if selected_voice == "peter" or selected_voice == "all":
                print("😂 Peter: 'That was fun! Same time tomorrow?'")
            if selected_voice == "scarlett" or selected_voice == "all":
                print("💫 Scarlett: 'Thank you for this fascinating experience.'")
            break
        except Exception as e:
            print(f"❌ Session error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    print("🎬 MULTI-CELEBRITY AI COMMENTARY SYSTEM")
    print("🎭 David Attenborough | Morgan Freeman | Peter Griffin | Scarlett Johansson")
    print("🎙️ Unique Voices | Distinct Personalities | Rich Multi-Perspective Commentary")
    print("=" * 80)
    main()
