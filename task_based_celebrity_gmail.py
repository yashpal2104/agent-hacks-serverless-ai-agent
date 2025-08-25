#!/usr/bin/env python3
"""
🎭📧🔊 Celebrity Gmail Reader - NATURAL AI VOICES
=================================================
Using Google's advanced text-to-speech for human-like celebrity voices!
"""

import os
import json
import tempfile
import pygame
from dotenv import load_dotenv
import google.generativeai as genai

# Try importing Google Cloud TTS (fallback to pyttsx3 if not available)
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    import pyttsx3
    GOOGLE_TTS_AVAILABLE = False

from portia import (
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
    PlanRunState,
    Portia,
    PortiaToolRegistry,
    default_config,
)

load_dotenv(override=True)

class AdvancedCelebrityVoice:
    def __init__(self):
        """Initialize advanced TTS with natural voices"""
        
        if GOOGLE_TTS_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            print("🎙️ Google Cloud TTS detected - using premium natural voices!")
            self.use_google_tts = True
            self.tts_client = texttospeech.TextToSpeechClient()
            self.setup_google_voices()
        else:
            print("🔊 Using improved pyttsx3 with best available voices")
            self.use_google_tts = False
            self.engine = pyttsx3.init()
            self.setup_local_voices()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Stop functionality
        self.is_speaking = False
        
    def setup_google_voices(self):
        """Setup Google Cloud TTS voices with authentic celebrity configurations"""
        self.celebrity_voices = {
            "David Attenborough": {
                'language_code': 'en-GB',
                'name': 'en-GB-Journey-D',  # Premium British voice
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 0.8,
                'pitch': 0.0,
                'personality': "nature-loving, educational, calming narrator",
                'style': "descriptive and soothing",
                'voice_description': "Speak with a gentle, breathy, and awe-inspired tone. Use a refined British accent, soft and curious, as though narrating a nature documentary. Pace your words slowly and deliberately, pausing to let moments of wonder sink in."
            },
            "Morgan Freeman": {
                'language_code': 'en-US',
                'name': 'en-US-Journey-D',  # Premium deep male voice
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 0.75,
                'pitch': -2.0,
                'personality': "wise, calm, authoritative narrator",
                'style': "deep and thoughtful",
                'voice_description': "Speak with a deep, steady, and resonant tone. Pause often for dramatic effect. Deliver sentences as though you are narrating something profound about life, with wisdom and calm authority."
            },
            "Scarlett Johansson": {
                'language_code': 'en-US',
                'name': 'en-US-Journey-F',  # Premium female voice
                'gender': texttospeech.SsmlVoiceGender.FEMALE,
                'speaking_rate': 0.9,
                'pitch': 0.0,
                'personality': "confident, witty, sophisticated actress",
                'style': "thoughtful and articulate",
                'voice_description': "Speak in a smooth, slightly husky and modern voice. Keep your pace gentle, with a calm confidence. Add a touch of warmth and curiosity in your tone, as if you are speaking closely to one person."
            },
            "Peter Griffin": {
                'language_code': 'en-US',
                'name': 'en-US-Casual-K',  # Casual voice for comedy
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 1.3,
                'pitch': 8.0,  # Higher pitch for Peter Griffin
                'personality': "humorous, relatable, down-to-earth family man",
                'style': "casual and funny",
                'voice_description': "Speak with a high-pitched, nasal, and slightly whiny voice characteristic of Peter Griffin. Add spontaneous expressions and use Peter's signature style with that distinctive high-pitched, cartoonish quality."
            }
        }
    
    def setup_local_voices(self):
        """Setup local voices with better settings"""
        voices = self.engine.getProperty('voices')
        
        # Find the best English voices
        english_voices = []
        for voice in voices:
            if 'english' in voice.name.lower() or 'en-' in voice.id.lower():
                english_voices.append(voice)
        
        print(f"🔍 Found {len(english_voices)} English voices")
        for i, voice in enumerate(english_voices[:5]):
            print(f"  {i}: {voice.name}")
        
        self.english_voices = english_voices
        
        # Better voice settings
        self.celebrity_configs = {
            "David Attenborough": {'rate': 160, 'volume': 0.9, 'voice_idx': 0},
            "Morgan Freeman": {'rate': 145, 'volume': 0.95, 'voice_idx': 1},
            "Scarlett Johansson": {'rate': 170, 'volume': 0.85, 'voice_idx': 2},
            "Peter Griffin": {'rate': 190, 'volume': 1.0, 'voice_idx': 0}
        }
    
    def generate_google_speech(self, text, celebrity_name):
        """Generate speech using Google Cloud TTS (very natural)"""
        voice_config = self.celebrity_voices[celebrity_name]
        
        # Set up the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build voice selection
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name'],
            ssml_gender=voice_config['gender']
        )
        
        # Configure audio
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_config['speaking_rate'],
            pitch=voice_config['pitch']
        )
        
        # Generate speech
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content
    
    def generate_local_speech(self, text, celebrity_name):
        """Generate speech using local TTS"""
        config = self.celebrity_configs.get(celebrity_name, self.celebrity_configs["David Attenborough"])
        
        # Configure voice
        self.engine.setProperty('rate', config['rate'])
        self.engine.setProperty('volume', config['volume'])
        
        # Select voice
        if self.english_voices:
            voice_idx = min(config['voice_idx'], len(self.english_voices) - 1)
            selected_voice = self.english_voices[voice_idx]
            self.engine.setProperty('voice', selected_voice.id)
            print(f"🎤 Using voice: {selected_voice.name}")
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        self.engine.save_to_file(text, temp_path)
        self.engine.runAndWait()
        
        return temp_path
    
    def speak_as_celebrity(self, text, celebrity_name):
        """Generate and play natural celebrity speech"""
        print(f"🎬 {celebrity_name} is preparing to speak naturally...")
        
        self.is_speaking = True
        
        try:
            if self.use_google_tts:
                # Generate with Google TTS (very natural)
                print("🎙️ Generating with Google's premium natural voice...")
                audio_content = self.generate_google_speech(text, celebrity_name)
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(audio_content)
                temp_file.close()
                
                # Play audio
                print(f"🔊 {celebrity_name} is speaking naturally!")
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy() and self.is_speaking:
                    pygame.time.wait(100)
                
                # Cleanup
                os.unlink(temp_file.name)
                
            else:
                # Use local TTS
                print("🎤 Generating with improved local voice...")
                audio_path = self.generate_local_speech(text, celebrity_name)
                
                # Play audio
                print(f"🔊 {celebrity_name} is speaking!")
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                
                # Wait for playback
                while pygame.mixer.music.get_busy() and self.is_speaking:
                    pygame.time.wait(100)
                
                # Cleanup
                os.unlink(audio_path)
            
            if self.is_speaking:
                print(f"✅ {celebrity_name} finished speaking naturally!")
            else:
                print(f"⏹️ {celebrity_name} was stopped")
                
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
            print("Falling back to simple text display...")
            print(f"\n🗣️ {celebrity_name} says:")
            print("─" * 40)
            print(text)
            print("─" * 40)
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech playback"""
        self.is_speaking = False
        try:
            pygame.mixer.music.stop()
            print("⏹️ Speech stopped")
        except:
            pass

def setup_content_generator():
    """Setup celebrity content generation"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != 'dummy_key_for_testing':
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"⚠️ Content generator unavailable: {e}")
    return None

def generate_celebrity_script(voice_model, celebrity_name, gmail_content, voice_engine=None):
    """Generate natural celebrity conversation script with voice-specific instructions"""
    
    # Get voice description if available
    voice_description = ""
    if voice_engine and hasattr(voice_engine, 'celebrity_voices') and celebrity_name in voice_engine.celebrity_voices:
        voice_info = voice_engine.celebrity_voices[celebrity_name]
        voice_description = voice_info.get('voice_description', '')
        personality = voice_info.get('personality', '')
        style = voice_info.get('style', '')
    
    prompts = {
        "David Attenborough": f"""You are David Attenborough. {voice_description}

Read through these Gmail emails as if you're genuinely fascinated by this person's professional journey. Use your natural warmth and curiosity. Keep it conversational and authentic - speak as if you're having a gentle conversation with someone you find genuinely interesting.

Focus on their career development, the companies they're reaching out to, and their academic journey. Speak naturally about each key theme you see in their emails.""",
        
        "Morgan Freeman": f"""You are Morgan Freeman. {voice_description}

Read through these Gmail emails as if you're having a genuine conversation with someone you care about. Use your natural wisdom and warmth. Reflect on this person's journey with the thoughtful perspective that comes naturally to you.

Speak about their professional growth, their networking efforts, and their determination. Make it feel like you're offering gentle wisdom about their path.""",
        
        "Scarlett Johansson": f"""You are Scarlett Johansson. {voice_description}

Read through these Gmail emails as if you're genuinely interested in this person's story. Be authentic, articulate, and naturally conversational. Speak with the confidence and warmth that comes naturally to you.

Talk about their professional ambitions, their approach to opportunities, and what you find impressive about their journey.""",
        
        "Peter Griffin": f"""You are Peter Griffin. {voice_description}

Read through these Gmail emails in your characteristic Peter Griffin style. Keep it natural and conversational while staying true to your personality. 

Look at this person's emails about jobs and meetings and school stuff, and talk about it the way Peter would - with that mix of humor and surprisingly genuine moments."""
    }
    
    prompt = prompts.get(celebrity_name, prompts["David Attenborough"])
    
    if voice_model:
        try:
            full_prompt = f"""{prompt}

Gmail content to discuss:
{gmail_content}

Speak naturally as {celebrity_name} about what you see in these emails:"""
            
            response = voice_model.generate_content(full_prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Script generation error: {e}")
    
    return f"Hi there! This is {celebrity_name}. Here's what I found in your Gmail: {gmail_content}"

def main():
    print("🎭📧🔊 NATURAL CELEBRITY GMAIL READER")
    print("=" * 45)
    print("Premium natural voices for celebrity email reading!")
    print()
    
    # Setup
    content_model = setup_content_generator()
    voice_engine = AdvancedCelebrityVoice()
    
    celebrities = {
        "david": "David Attenborough",
        "morgan": "Morgan Freeman", 
        "scarlett": "Scarlett Johansson",
        "peter": "Peter Griffin"
    }
    
    # Get inputs
    print("\n📧 EMAIL INPUT")
    sender_email = input("Enter sender email: ").strip()
    
    print("\n🎭 CELEBRITY SELECTION")
    for key, name in celebrities.items():
        print(f"  {key}: {name}")
    celebrity_key = input("Select celebrity: ").strip().lower()
    
    # Flexible celebrity selection with partial matches
    celebrity_name = "David Attenborough"  # default
    
    if celebrity_key in celebrities:
        celebrity_name = celebrities[celebrity_key]
    else:
        # Handle partial matches and common variations
        for key, name in celebrities.items():
            if celebrity_key.startswith(key[:3]) or key.startswith(celebrity_key[:3]):
                celebrity_name = name
                print(f"✅ Selected: {celebrity_name}")
                break
        else:
            # Check for name matches
            celebrity_key_words = celebrity_key.replace(" ", "").lower()
            for key, name in celebrities.items():
                name_words = name.replace(" ", "").lower()
                if celebrity_key_words in name_words or name_words.startswith(celebrity_key_words[:3]):
                    celebrity_name = name
                    print(f"✅ Selected: {celebrity_name}")
                    break
            else:
                print(f"⚠️ '{celebrity_key}' not recognized, using default: {celebrity_name}")
    
    # Setup Portia with task-based approach and working Claude model
    print("\n🔧 Setting up Portia...")
    config = default_config()
    
    # Configure working Claude model to avoid 404 errors
    working_model = "anthropic/claude-3-5-haiku-20241022"
    config.models.default_model = working_model
    config.models.planning_model = working_model
    config.models.execution_model = working_model
    config.models.introspection_model = working_model
    
    portia = Portia(tools=PortiaToolRegistry(config), config=config)
    print("✅ Portia configured with working Claude model and Gmail tools")
    
    # Create Gmail reading task
    task = f"Search Gmail for emails from {sender_email} and provide a detailed summary of each email. Read each email in order and provide the content clearly."
    
    print(f"\n� Running Gmail task for {sender_email}...")
    
    try:
        plan_run = portia.run(task)
        
        # Handle clarifications (all types)
        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            print("\nPlease resolve the following clarifications to continue")
            for clarification in plan_run.get_outstanding_clarifications():
                # Action clarifications
                if isinstance(clarification, ActionClarification):
                    print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
                    print(clarification.action_url)
                    input("Press Enter to continue...")
                
                # Input clarifications  
                elif isinstance(clarification, InputClarification):
                    user_input = input(f"{clarification.prompt}: ")
                    clarification.respond(user_input)
                
                # Multiple choice clarifications
                elif isinstance(clarification, MultipleChoiceClarification):
                    print(f"{clarification.prompt}")
                    for i, option in enumerate(clarification.options):
                        print(f"  {i+1}. {option}")
                    choice = input("Select option (number): ").strip()
                    try:
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(clarification.options):
                            clarification.respond(clarification.options[choice_idx])
                        else:
                            print("Invalid choice, using first option")
                            clarification.respond(clarification.options[0])
                    except ValueError:
                        print("Invalid input, using first option")
                        clarification.respond(clarification.options[0])
            
            # Resume after clarifications
            plan_run = portia.resume(plan_run)
        
        print(f"� Task status: {plan_run.state}")
        
        # Extract Gmail content from task result
        gmail_content = ""
        if hasattr(plan_run, 'result') and plan_run.result:
            gmail_content = str(plan_run.result)
        elif hasattr(plan_run, 'outputs') and plan_run.outputs:
            gmail_content = str(plan_run.outputs)
        
        # Fallback: extract from plan_run data
        if not gmail_content:
            plan_data = str(plan_run)
            if any(keyword in plan_data.lower() for keyword in ['email', 'gmail', 'devops', 'job', 'subject']):
                gmail_content = plan_data
        
        # Check if we got Gmail data
        if gmail_content and len(gmail_content.strip()) > 50:
            print("✅ Gmail content retrieved successfully!")
            print(f"📊 Content length: {len(gmail_content)} characters")
            
            # Generate celebrity script with voice descriptions
            print(f"✍️ Creating {celebrity_name}'s natural conversation...")
            script = generate_celebrity_script(content_model, celebrity_name, gmail_content, voice_engine)
            
            # Show script preview  
            print(f"\n📜 {celebrity_name}'s Script Preview:")
            print("─" * 50)
            preview = script[:300] + "..." if len(script) > 300 else script
            print(preview)
            print("─" * 50)
            
            # Generate natural speech
            print(f"\n🎬 Ready for {celebrity_name}'s NATURAL voice with premium Google TTS!")
            input("Press Enter to hear the natural AI voice reading your emails...")
            
            voice_engine.speak_as_celebrity(script, celebrity_name)
            
            print(f"\n🎉 {celebrity_name} spoke your emails with natural AI voice!")
            
        else:
            print("📭 No Gmail content found or content too short")
            if len(str(plan_run)) > 100:
                print("Debug - Raw result sample:")
                print(str(plan_run)[:500] + "...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
