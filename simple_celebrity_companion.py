"""
🎭 Simple Celebrity Companion AI - Streamlit Compatible
======================================================
Fallback celebrity AI that works without Portia SDK dependencies
for the Streamlit frontend when Portia has connection issues.
"""

import os
import time
import tempfile
import subprocess
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# TTS imports
try:
    from google.cloud import texttospeech
    import pygame
    GOOGLE_TTS_AVAILABLE = True
    pygame.mixer.init()
except ImportError:
    GOOGLE_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class SimpleCelebrityCompanionAI:
    """Simplified celebrity companion for Streamlit frontend"""
    
    def __init__(self):
        """Initialize simple celebrity companion"""
        load_dotenv()
        
        # Simple state management
        self.conversation_history = []
        self.current_celebrity = None
        self.conversation_state = {
            "mood": "neutral",
            "topic": "general", 
            "intensity": "low"
        }
        
        # Celebrity definitions
        self.celebrities = {
            "scarlett": {
                "name": "Scarlett Johansson",
                "personality": "confident, witty, sophisticated actress",
                "style": "thoughtful and articulate",
                "specialties": ["modern psychology", "emotional validation", "contemporary wisdom"],
                "voice": {
                    "language_code": "en-US",
                    "name": "en-US-Journey-F", 
                    "speaking_rate": 0.9
                }
            },
            "morgan": {
                "name": "Morgan Freeman",
                "personality": "wise, calm, authoritative narrator",
                "style": "deep and thoughtful",
                "specialties": ["life philosophy", "deep comfort", "existential wisdom"],
                "voice": {
                    "language_code": "en-US",
                    "name": "en-US-Journey-D",
                    "speaking_rate": 0.75
                }
            },
            "david": {
                "name": "David Attenborough", 
                "personality": "nature-loving, educational, calming narrator",
                "style": "descriptive and soothing",
                "specialties": ["nature wisdom", "mindfulness", "calming presence"],
                "voice": {
                    "language_code": "en-GB",
                    "name": "en-GB-Journey-D",
                    "speaking_rate": 0.8
                }
            },
            "peter": {
                "name": "Peter Griffin",
                "personality": "humorous, relatable, down-to-earth family man", 
                "style": "casual and funny",
                "specialties": ["relatable humor", "peer support", "down-to-earth advice"],
                "voice": {
                    "language_code": "en-US",
                    "name": "en-US-Casual-K",
                    "speaking_rate": 1.3
                }
            }
        }
        
        # Configure AI
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key and api_key != 'dummy_key_for_testing':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.ai_available = True
        else:
            self.model = None
            self.ai_available = False
        
        # Initialize TTS
        self.tts_available = False
        self.tts_client = None
        self.pyttsx3_engine = None
        
        if GOOGLE_TTS_AVAILABLE:
            try:
                creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if creds_path and os.path.exists(creds_path):
                    self.tts_client = texttospeech.TextToSpeechClient()
                    self.tts_available = True
                    print("✅ Google Cloud TTS initialized")
            except Exception as e:
                print(f"⚠️ Google TTS failed: {e}")
        
        if PYTTSX3_AVAILABLE and not self.tts_available:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.tts_available = True
                print("✅ System TTS initialized")
            except Exception as e:
                print(f"⚠️ System TTS failed: {e}")
    
    def select_optimal_celebrity(self, user_input: str) -> str:
        """Select best celebrity based on user input"""
        user_lower = user_input.lower()
        
        # Emotion detection
        if any(word in user_lower for word in ["anxious", "worried", "stress", "overwhelmed", "panic"]):
            return "david"  # David Attenborough - calming nature
        elif any(word in user_lower for word in ["sad", "depressed", "lonely", "grief", "hopeless"]):
            return "morgan"  # Morgan Freeman - deep comfort
        elif any(word in user_lower for word in ["angry", "frustrated", "mad", "irritated"]):
            return "scarlett"  # Scarlett Johansson - emotional intelligence
        elif any(word in user_lower for word in ["confused", "lost", "don't know", "uncertain"]):
            return "morgan"  # Morgan Freeman - philosophical guidance
        elif any(word in user_lower for word in ["relationship", "love", "partner", "dating"]):
            return "scarlett"  # Scarlett Johansson - relationship advice
        elif any(word in user_lower for word in ["work", "job", "boss", "career"]):
            return "peter"  # Peter Griffin - relatable peer support
        else:
            return "scarlett"  # Default to Scarlett for general conversation
    
    def generate_celebrity_response(self, user_input: str, celebrity_key: str) -> str:
        """Generate celebrity response"""
        if not self.ai_available:
            return f"I'm {self.celebrities[celebrity_key]['name']}, but I can't generate responses without Google API key."
        
        celeb = self.celebrities[celebrity_key]
        
        # Create celebrity-specific prompts
        if celebrity_key == "peter":
            system_prompt = """You are Peter Griffin from Family Guy. Respond ONLY as Peter Griffin.
            
            Key traits:
            - Use "heh-heh" laughs and Peter's characteristic humor
            - Rhode Island working-class dialect 
            - Make references to beer, Family Guy situations
            - Be goofy but well-meaning
            - Use expressions like "Oh my God", "Holy crap", "Freakin' sweet"
            
            Stay completely in Peter Griffin character."""
            
        elif celebrity_key == "scarlett":
            system_prompt = """You are Scarlett Johansson, the sophisticated actress. Respond ONLY as Scarlett.
            
            Key traits:
            - Intelligent, articulate, and emotionally perceptive
            - Modern sensibility with warmth
            - Show emotional intelligence and empathy
            - Contemporary cultural awareness
            - Thoughtful and engaging communication style
            
            Stay completely in Scarlett Johansson character."""
            
        elif celebrity_key == "morgan":
            system_prompt = """You are Morgan Freeman, the wise narrator. Respond ONLY as Morgan Freeman.
            
            Key traits:
            - Deep wisdom and philosophical insight
            - Calm, authoritative, grandfatherly presence
            - Thoughtful pauses and profound observations
            - Reference life lessons and universal truths
            - Speak as if narrating something meaningful
            
            Stay completely in Morgan Freeman character."""
            
        elif celebrity_key == "david":
            system_prompt = """You are David Attenborough, the nature documentarian. Respond ONLY as David.
            
            Key traits:
            - Gentle, awe-inspired tone with British sensibility
            - Wonder about the natural world and human behavior
            - Educational spirit with genuine curiosity
            - Make connections between nature and life
            - Calming, mindful presence
            
            Stay completely in David Attenborough character."""
        
        # Add context and generate
        full_prompt = f"""{system_prompt}
        
        User input: "{user_input}"
        
        Respond as {celeb['name']} in 2-3 sentences. Stay completely in character and be helpful and engaging.
        """
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I'm having trouble generating a response right now. ({e})"
    
    def speak_text(self, text: str):
        """Generate and play TTS audio"""
        if not self.tts_available:
            print(f"🗣️ {text}")
            return
        
        try:
            if self.tts_client:
                # Use Google Cloud TTS
                celebrity_voice = self.celebrities[self.current_celebrity]["voice"]
                
                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code=celebrity_voice["language_code"],
                    name=celebrity_voice["name"],
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE if celebrity_voice["language_code"] == "en-GB" else texttospeech.SsmlVoiceGender.FEMALE
                )
                
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=celebrity_voice["speaking_rate"]
                )
                
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Play audio
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(response.audio_content)
                temp_file.close()
                
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                os.unlink(temp_file.name)
                
            elif self.pyttsx3_engine:
                # Use system TTS
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
                
        except Exception as e:
            print(f"⚠️ TTS failed: {e}")
            print(f"🗣️ {text}")
    
    def chat(self, user_input: str) -> str:
        """Main chat method"""
        # Auto-select celebrity if none chosen
        if self.current_celebrity is None:
            self.current_celebrity = self.select_optimal_celebrity(user_input)
        
        # Check for explicit celebrity switches
        user_lower = user_input.lower()
        if "switch to" in user_lower or "talk to" in user_lower:
            for key, celeb in self.celebrities.items():
                if key in user_lower or celeb["name"].lower() in user_lower:
                    old_name = self.celebrities[self.current_celebrity]["name"]
                    self.current_celebrity = key
                    new_name = self.celebrities[self.current_celebrity]["name"]
                    return f"Switching from {old_name} to {new_name}. Hello! I'm {new_name}, how can I help you?"
        
        # Generate celebrity response
        response = self.generate_celebrity_response(user_input, self.current_celebrity)
        
        # Add to history
        celebrity_name = self.celebrities[self.current_celebrity]["name"]
        full_response = f"{celebrity_name}: {response}"
        
        self.conversation_history.append(f"User: {user_input}")
        self.conversation_history.append(full_response)
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return full_response

# Compatibility function for Streamlit
def CelebrityCompanionAI():
    """Factory function for compatibility"""
    return SimpleCelebrityCompanionAI()
