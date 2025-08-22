"""
Celebrity Companion AI - Portia SDK Multi-Agent Edition
=======================================================
Empathetic AI with authentic celebrity voices for emotional support.
Powered by Portia SDK's three-agent architecture and Google Cloud TTS.

ARCHITECTURE:
- Portia SDK for multi-agent orchestration and intelligent planning
- Planning Agent: Creates conversation strategies and celebrity selection
- Execution Agent: Generates responses and handles TTS operations
- Introspection Agent: Monitors conversation state and adapts strategies
- Google Gemini AI for intelligent celebrity responses
- Google Cloud TTS for authentic celebrity voices

CELEBRITY AGENTS:
- David Attenborough: Nature-based comfort and mindfulness
- Morgan Freeman: Philosophical wisdom and life perspective  
- Scarlett Johansson: Modern psychology and emotional validation
- Peter Griffin: Relatable humor and peer support
"""

import os
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Portia SDK imports
try:
    from portia import Portia
    from portia.plan import Plan, Step, PlanInput  # Use PlanInput instead of Input
    from portia.execution_agents.base_execution_agent import BaseExecutionAgent
    from portia.execution_agents.default_execution_agent import DefaultExecutionAgent
    from portia.tool import Tool, ToolRunContext
    from portia.config import Config
    from portia.end_user import EndUser
    from portia.storage import AgentMemory
    from portia.plan_run import PlanRun
    from typing import TYPE_CHECKING
    
    if TYPE_CHECKING:
        # Import types for annotations only
        from portia.tool import Tool as ToolType
        from portia.tool import ToolRunContext as ToolRunContextType
        from portia.end_user import EndUser as EndUserType
    
    PORTIA_AVAILABLE = True
    print("✅ Portia SDK imported successfully")
except ImportError as e:
    print(f"❌ Portia SDK not available: {e}")
    PORTIA_AVAILABLE = False
    # Define dummy classes for when Portia is not available
    Tool = object
    ToolRunContext = object
    DefaultExecutionAgent = object
    Config = object
    EndUser = object
    AgentMemory = object
    PlanRun = object
    Plan = object

# TTS imports
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    print("❌ Google Cloud TTS not available")
    GOOGLE_TTS_AVAILABLE = False

class CelebrityResponseTool(Tool):
    """Portia Tool for generating celebrity responses"""
    
    def __init__(self, celebrities, model, current_celebrity_getter):
        super().__init__()
        self.celebrities = celebrities
        self.model = model
        self.get_current_celebrity = current_celebrity_getter
        
    @property
    def name(self) -> str:
        return "celebrity_response_generator"
        
    @property
    def description(self) -> str:
        return "Generates authentic responses as specific celebrity personalities"
    
    def run(self, context, user_input: str) -> str:
        """Generate celebrity response using the specified personality"""
        current_celebrity = self.get_current_celebrity()
        celeb = self.celebrities[current_celebrity]
        
        # Build celebrity-specific prompt
        if current_celebrity == "peter":
            system_prompt = f"""You are Peter Griffin from Family Guy. You are speaking as Peter Griffin ONLY.
            Key traits: Use "heh-heh" laughs, Rhode Island dialect, beer references, goofy but well-meaning.
            DO NOT speak like other celebrities. You are ONLY Peter Griffin."""
            
        elif current_celebrity == "scarlett":
            system_prompt = f"""You are Scarlett Johansson, the sophisticated actress.
            Key traits: Intelligence, wit, emotional intelligence, contemporary culture references.
            DO NOT speak like other celebrities. You are ONLY Scarlett Johansson."""
            
        elif current_celebrity == "morgan":
            system_prompt = f"""You are Morgan Freeman, the wise narrator.
            Key traits: Deep wisdom, philosophical insight, thoughtful pauses, life lessons.
            DO NOT speak like other celebrities. You are ONLY Morgan Freeman."""
            
        elif current_celebrity == "david":
            system_prompt = f"""You are David Attenborough, the nature documentarian.
            Key traits: Wonder about nature, gentle British tone, educational spirit, curiosity.
            DO NOT speak like other celebrities. You are ONLY David Attenborough."""
        
        full_prompt = f"""{system_prompt}
        
        User input: "{user_input}"
        Respond as {celeb['name']} in 2-3 sentences, staying completely in character.
        """
        
        # Generate response
        response = self.model.generate_content(full_prompt)
        return response.text.strip()


class CelebrityExecutionAgent(DefaultExecutionAgent):
    """Custom execution agent for celebrity response generation following Portia SDK patterns"""
    
    def __init__(self, plan, plan_run, config, agent_memory, 
                 end_user, celebrity_tool, execution_hooks=None):
        """Initialize the celebrity execution agent"""
        super().__init__(
            plan=plan,
            plan_run=plan_run, 
            config=config,
            agent_memory=agent_memory,
            end_user=end_user,
            tool=celebrity_tool,
            execution_hooks=execution_hooks
        )
        self.celebrity_tool = celebrity_tool

class CelebrityCompanionAI:
    def __init__(self):
        """Initialize with Portia SDK integration"""
        # Load environment
        load_dotenv()
        
        # Initialize Portia SDK with proper configuration
        self.portia = None
        self.portia_config = None
        self.end_user = None
        self.agent_memory = None
        
        if PORTIA_AVAILABLE:
            try:
                # Initialize Portia components properly
                self.portia_config = Config()  # Use default config
                self.end_user = EndUser(id="celebrity_user", name="Celebrity Companion User")
                self.agent_memory = AgentMemory()  # Initialize agent memory
                
                # Create custom celebrity response tool
                self.celebrity_tool = CelebrityResponseTool(
                    celebrities=self.celebrities,
                    model=self.model,
                    current_celebrity_getter=lambda: self.current_celebrity
                )
                
                print("✅ Portia SDK initialized with proper configuration")
            except Exception as e:
                print(f"⚠️  Portia SDK initialization failed: {str(e)}")
                print("🔄 Will use direct Gemini mode")
                self.portia = None
        
        # Simple state using basic data structures
        self.conversation_history = []
        self.current_celebrity = None  # Will be set dynamically based on user analysis
        self.conversation_state = {
            "mood": "neutral",
            "topic": "general",
            "intensity": "low",
            "last_switch": None,
            "first_interaction": True
        }
        
        # Check systems
        self.audio_available = self.check_audio()
        
        # Celebrity data - simple dictionary structure
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
                },
                "voice_description": "Speak in a smooth, slightly husky and modern voice. Keep your pace gentle, with a calm confidence. Add a touch of warmth and curiosity in your tone, as if you are speaking closely to one person."
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
                },
                "voice_description": "Speak with a deep, steady, and resonant tone. Pause often for dramatic effect. Deliver sentences as though you are narrating something profound about life, with wisdom and calm authority."
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
                },
                "voice_description": "Speak with a gentle, breathy, and awe-inspired tone. Use a refined British accent, soft and curious, as though narrating a nature documentary. Pace your words slowly and deliberately, pausing to let moments of wonder sink in. Occasionally build excitement when describing something extraordinary."
            },
            "peter": {
                "name": "Peter Griffin",
                "personality": "humorous, relatable, down-to-earth family man",
                "style": "casual and funny",
                "specialties": ["relatable humor", "peer support", "down-to-earth advice", "snarky"],
                "voice": {
                    "language_code": "en-US",
                    "name": "en-US-Casual-K",
                    "speaking_rate": 1.3,
                    "pitch": "+8.0st"  # Higher pitch for Peter Griffin
                },
                "voice_description": "Speak with a high-pitched, nasal, and slightly whiny voice characteristic of Peter Griffin. Add spontaneous laughter ('heh-heh', 'nyeh-heh-heh') and goofy asides. Use a Rhode Island-style American accent with that distinctive high-pitched, cartoonish quality. Occasionally trail off on silly tangents and use Peter's signature expressions like 'Oh my God', 'Holy crap', and 'Freakin' sweet!'"
            }
        }
        
        # Configure AI
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize TTS
        self.tts_client = None
        self.tts_available = False
        
        if GOOGLE_TTS_AVAILABLE:
            try:
                if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                    self.tts_client = texttospeech.TextToSpeechClient()
                    self.tts_available = True
                    print("✅ Google Cloud TTS initialized")
                else:
                    print("⚠️  Google Cloud TTS requires GOOGLE_APPLICATION_CREDENTIALS environment variable")
                    print("🔄 Voice will be text-only")
            except Exception as e:
                print(f"⚠️  Google Cloud TTS failed: {str(e)}")
                print("🔄 Voice will be text-only")
        self.tts_client = None
        self.tts_available = False
        
        if GOOGLE_TTS_AVAILABLE:
            try:
                # Check for Google Cloud credentials
                if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                    self.tts_client = texttospeech.TextToSpeechClient()
                    self.tts_available = True
                    print("✅ Google Cloud TTS initialized")
                else:
                    print("⚠️  Google Cloud TTS requires GOOGLE_APPLICATION_CREDENTIALS environment variable")
                    print("🔄 Voice will be text-only")
            except Exception as e:
                print(f"⚠️  Google Cloud TTS failed: {str(e)}")
                print("🔄 Voice will be text-only")
    
    def check_audio(self):
        """Check if audio playback is available"""
        try:
            result = subprocess.run(['which', 'paplay'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Audio system: paplay available")
                return True
            else:
                result = subprocess.run(['which', 'aplay'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Audio system: aplay available")
                    return True
                else:
                    print("❌ Audio system: no audio player found")
                    return False
        except Exception:
            print("❌ Audio system: check failed")
            return False
    
    def _simple_response_generation(self, user_input: str, context_analysis: Dict[str, Any]) -> str:
        """Simple response generation for fallback"""
        celeb = self.celebrities[self.current_celebrity]
        
        # Build celebrity-specific prompt (same as the tool but for fallback)
        if self.current_celebrity == "peter":
            system_prompt = f"""You are Peter Griffin from Family Guy. You are speaking as Peter Griffin ONLY.
            Key traits: Use "heh-heh" laughs, Rhode Island dialect, beer references, goofy but well-meaning.
            DO NOT speak like other celebrities. You are ONLY Peter Griffin."""
            
        elif self.current_celebrity == "scarlett":
            system_prompt = f"""You are Scarlett Johansson, the sophisticated actress.
            Key traits: Intelligence, wit, emotional intelligence, contemporary culture references.
            DO NOT speak like other celebrities. You are ONLY Scarlett Johansson."""
            
        elif self.current_celebrity == "morgan":
            system_prompt = f"""You are Morgan Freeman, the wise narrator.
            Key traits: Deep wisdom, philosophical insight, thoughtful pauses, life lessons.
            DO NOT speak like other celebrities. You are ONLY Morgan Freeman."""
            
        elif self.current_celebrity == "david":
            system_prompt = f"""You are David Attenborough, the nature documentarian.
            Key traits: Wonder about nature, gentle British tone, educational spirit, curiosity.
            DO NOT speak like other celebrities. You are ONLY David Attenborough."""
        
        full_prompt = f"""{system_prompt}
        
        User input: "{user_input}"
        Respond as {celeb['name']} in 2-3 sentences, staying completely in character.
        """
        
        response = self.model.generate_content(full_prompt)
        return response.text.strip()
    
    def select_optimal_celebrity(self, user_input: str) -> str:
        """Simple celebrity selection based on user input analysis"""
        user_lower = user_input.lower()
        
        # Simple emotion/topic detection for celebrity selection
        if any(word in user_lower for word in ["stress", "anxious", "worried", "overwhelm"]):
            return "david"  # Calming nature wisdom
        elif any(word in user_lower for word in ["sad", "lonely", "grief", "confused"]):
            return "morgan"  # Deep wisdom and comfort
        elif any(word in user_lower for word in ["angry", "frustrated", "relationship"]):
            return "scarlett"  # Emotional intelligence  
        else:
            return "peter"  # Default to humor and relatability
    
    def _simple_context_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback context analysis without Portia"""
        user_lower = user_input.lower()
        
        # Simple mood detection
        mood_keywords = {
            "anxiety": ["anxious", "worried", "nervous", "stress", "overwhelmed"],
            "sadness": ["sad", "depressed", "lonely", "grief", "melancholy"],
            "anger": ["angry", "frustrated", "mad", "irritated", "annoyed"],
            "joy": ["happy", "excited", "thrilled", "delighted", "ecstatic"]
        }
        
        detected_mood = "neutral"
        for mood, keywords in mood_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_mood = mood
                break
        
        # Simple topic detection
        topic_keywords = {
            "relationships": ["relationship", "partner", "friend", "family", "love"],
            "work": ["work", "job", "career", "boss", "colleague"],
            "health": ["health", "sick", "pain", "doctor", "medical"],
            "personal": ["personal", "myself", "I", "me", "my life"]
        }
        
        detected_topic = "general"
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_topic = topic
                break
        
        return {
            "mood": detected_mood,
            "topic": detected_topic,
            "intensity": "medium" if detected_mood != "neutral" else "low",
            "recommended_celebrity": self._get_celebrity_for_context(detected_mood, detected_topic),
            "response_strategy": "empathetic" if detected_mood != "neutral" else "conversational"
        }
    
    def _get_celebrity_for_context(self, mood: str, topic: str) -> str:
        """Simple celebrity selection based on context"""
        if mood in ["anxiety", "overwhelm"]:
            return "david"  # Nature wisdom and calming
        elif mood in ["sadness", "grief"]:
            return "morgan"  # Deep comfort and wisdom
        elif mood in ["anger", "frustration"]:
            return "scarlett"  # Modern psychology
        elif topic == "relationships":
            return "scarlett"  # Emotional intelligence
        elif topic == "work":
            return "peter"  # Relatable peer support
        else:
            return "scarlett"  # Keep current if no clear match
    
    def select_optimal_celebrity(self, user_input: str) -> str:
        """Intelligently select the best celebrity based on user input analysis"""
        
        # Analyze the user's input for emotional content and context
        user_lower = user_input.lower()
        
        # Emotional state detection
        emotion_keywords = {
            "anxiety": ["anxious", "worried", "nervous", "stress", "overwhelmed", "panic", "fear", "scared"],
            "sadness": ["sad", "depressed", "lonely", "grief", "melancholy", "down", "blue", "hopeless"],
            "anger": ["angry", "frustrated", "mad", "irritated", "annoyed", "furious", "rage", "hate"],
            "joy": ["happy", "excited", "thrilled", "delighted", "ecstatic", "great", "wonderful"],
            "confusion": ["confused", "unsure", "uncertain", "lost", "don't know", "what to do"],
            "loneliness": ["alone", "lonely", "isolated", "no one", "by myself", "friendless"]
        }
        
        # Topic detection
        topic_keywords = {
            "relationships": ["relationship", "partner", "friend", "family", "love", "dating", "marriage", "breakup"],
            "work": ["work", "job", "career", "boss", "colleague", "office", "meeting", "deadline"],
            "health": ["health", "sick", "pain", "doctor", "medical", "hospital", "illness", "symptoms"],
            "personal_growth": ["growth", "improve", "better", "change", "transform", "evolve", "learn"],
            "life_philosophy": ["meaning", "purpose", "life", "existence", "why", "philosophy", "spiritual"]
        }
        
        # Detect primary emotion
        detected_mood = "neutral"
        mood_score = 0
        for mood, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            if score > mood_score:
                mood_score = score
                detected_mood = mood
        
        # Detect primary topic
        detected_topic = "general"
        topic_score = 0
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            if score > topic_score:
                topic_score = score
                detected_topic = topic
        
        # Determine intensity based on language
        intensity_indicators = ["very", "extremely", "really", "so", "too", "absolutely", "completely"]
        intensity = "low"
        if any(indicator in user_lower for indicator in intensity_indicators):
            intensity = "high"
        elif mood_score > 2 or topic_score > 2:
            intensity = "medium"
        
        # Update conversation state
        self.conversation_state.update({
            "mood": detected_mood,
            "topic": detected_topic,
            "intensity": intensity
        })
        
        # Select optimal celebrity based on analysis
        if detected_mood == "anxiety" or detected_mood == "overwhelm":
            return "david"  # David Attenborough - nature wisdom and calming presence
        elif detected_mood == "sadness" or detected_mood == "grief" or detected_mood == "loneliness":
            return "morgan"  # Morgan Freeman - deep comfort and existential wisdom
        elif detected_mood == "anger" or detected_mood == "frustration":
            return "scarlett"  # Scarlett Johansson - modern psychology and emotional validation
        elif detected_mood == "confusion":
            return "morgan"  # Morgan Freeman - philosophical guidance
        elif detected_topic == "relationships":
            return "scarlett"  # Scarlett Johansson - emotional intelligence
        elif detected_topic == "work":
            return "peter"  # Peter Griffin - relatable peer support
        elif detected_topic == "life_philosophy":
            return "morgan"  # Morgan Freeman - deep wisdom
        elif detected_topic == "personal_growth":
            return "scarlett"  # Scarlett Johansson - modern psychology
        else:
            # Default based on general mood
            if intensity == "high":
                return "david"  # Calming presence for high intensity
            elif intensity == "medium":
                return "scarlett"  # Balanced approach for medium intensity
            else:
                return "peter"  # Light approach for low intensity
    
    def _simple_response_generation(self, user_input: str, context_analysis: Dict[str, Any]) -> str:
        """Fallback response generation without Portia"""
        celeb = self.celebrities[self.current_celebrity]
        
        # Build very specific prompt for each celebrity to avoid personality mixing
        if self.current_celebrity == "peter":
            system_prompt = f"""You are Peter Griffin from Family Guy. You are speaking as Peter Griffin ONLY.
            
            Key traits:
            - Speak with Peter's characteristic "heh-heh" laughs
            - Use Rhode Island/Boston area working class dialect
            - Make references to beer, chicken fights, and Family Guy situations
            - Be goofy, well-meaning but not always bright
            - Add random tangents and non-sequiturs
            - Use Peter's typical expressions like "Oh my God", "Holy crap", "Freakin' sweet"
            
            DO NOT speak like Scarlett Johansson or any other celebrity.
            You are ONLY Peter Griffin responding as Peter Griffin would."""
            
        elif self.current_celebrity == "scarlett":
            system_prompt = f"""You are Scarlett Johansson, the sophisticated actress.
            
            Key traits:
            - Speak with intelligence, wit, and modern sensibility
            - Use thoughtful, articulate language
            - Show emotional intelligence and empathy
            - Reference contemporary culture and psychology
            - Maintain a warm but professional tone
            
            DO NOT speak like Peter Griffin or any other celebrity.
            You are ONLY Scarlett Johansson responding as she would."""
            
        elif self.current_celebrity == "morgan":
            system_prompt = f"""You are Morgan Freeman, the wise narrator.
            
            Key traits:
            - Speak with deep wisdom and philosophical insight
            - Use Morgan's characteristic thoughtful pauses and profound observations
            - Reference life lessons and universal truths
            - Maintain a calm, authoritative, grandfatherly presence
            - Speak as if narrating something meaningful
            
            DO NOT speak like Peter Griffin or any other celebrity.
            You are ONLY Morgan Freeman responding as he would."""
            
        elif self.current_celebrity == "david":
            system_prompt = f"""You are David Attenborough, the nature documentarian.
            
            Key traits:
            - Speak with wonder about the natural world
            - Use David's characteristic gentle, awe-inspired tone
            - Make connections between nature and human experience
            - Maintain a British accent in your word choices
            - Show genuine curiosity and educational spirit
            
            DO NOT speak like Peter Griffin or any other celebrity.
            You are ONLY David Attenborough responding as he would."""
        
        # Add context information
        full_prompt = f"""{system_prompt}
        
        Current situation:
        - User's mood: {context_analysis.get('mood', 'neutral')}
        - Conversation topic: {context_analysis.get('topic', 'general')}
        - Response should be: {context_analysis.get('response_strategy', 'conversational')}
        
        Keep responses 2-3 sentences and stay completely in character.
        CRITICAL: Only respond as {celeb['name']}, never mix personalities."""
        
        # Create context from conversation history
        context = f"{full_prompt}\n\nRecent conversation:\n"
        context += "\n".join(self.conversation_history[-4:])  # Keep last 2 exchanges
        context += f"\n{celeb['name']}:"
        
        # Generate response
        response = self.model.generate_content(context)
        celebrity_response = response.text.strip()
        
        return celebrity_response
    
    def switch_celebrity(self, celebrity_key):
        """Switch to a different celebrity"""
        if celebrity_key in self.celebrities:
            old_name = self.celebrities[self.current_celebrity]['name']
            self.current_celebrity = celebrity_key
            new_name = self.celebrities[self.current_celebrity]['name']
            
            # Update state
            self.conversation_state["last_switch"] = time.time()
            
            # Add transition message to history
            transition_msg = f"[Switched from {old_name} to {new_name}]"
            self.conversation_history.append(transition_msg)
            
            return f"✨ Switched to {new_name}"
        else:
            available = list(self.celebrities.keys())
            return f"❌ Celebrity not found. Available: {', '.join(available)}"
    
    def chat(self, user_input):
        """Main chat method using Portia multi-agent orchestration"""
        
        # FIRST: Check if user explicitly mentions a specific celebrity
        user_lower = user_input.lower()
        explicit_celebrity = None
        
        # Check for explicit celebrity mentions in user input
        celebrity_mentions = {
            "peter": ["peter griffin", "peter", "griffin"],
            "scarlett": ["scarlett johansson", "scarlett", "scarlet", "johansson"],
            "morgan": ["morgan freeman", "morgan", "freeman"],
            "david": ["david attenborough", "david", "attenborough"]
        }
        
        for key, variations in celebrity_mentions.items():
            for variation in variations:
                if variation in user_lower:
                    explicit_celebrity = key
                    break
            if explicit_celebrity:
                break
        
        # If user explicitly mentions a celebrity, switch to them
        if explicit_celebrity and explicit_celebrity != self.current_celebrity:
            self.current_celebrity = explicit_celebrity
            celeb_name = self.celebrities[explicit_celebrity]['name']
            print(f"🎭 Switched to {celeb_name} as requested")
            self.conversation_history.append(f"[User requested {celeb_name}]")
        
        # Check for general switching commands
        if any(switch_word in user_lower for switch_word in ['switch to', 'change to', 'talk to']) and not explicit_celebrity:
            for key in self.celebrities.keys():
                if key in user_lower or self.celebrities[key]['name'].lower() in user_lower:
                    return self.switch_celebrity(key)
        
        # Set default celebrity if none selected
        if self.current_celebrity is None:
            print("🧠 Analyzing user input to select optimal celebrity...")
            selected_celebrity = self.select_optimal_celebrity(user_input)
            self.current_celebrity = selected_celebrity
            celeb_name = self.celebrities[selected_celebrity]['name']
            print(f"🎭 Selected {celeb_name} based on your message")
            self.conversation_state["first_interaction"] = False
        
        # Add to conversation history
        self.conversation_history.append(f"User: {user_input}")
        
        # IMPORTANT: Lock the celebrity identity for this response
        response_celebrity = self.current_celebrity
        response_celebrity_name = self.celebrities[response_celebrity]['name']
        
        # Use proper Portia SDK execution if available
        if PORTIA_AVAILABLE and hasattr(self, 'celebrity_tool') and self.portia_config:
            try:
                # Create a proper Portia Plan with Step and Input
                celebrity_step = Step(
                    step_id="celebrity_response",
                    task=f"Generate response as {response_celebrity_name} to: {user_input}",
                    tool=self.celebrity_tool,
                    inputs=[
                        PlanInput(name="user_input", value=user_input, description="User's message")
                    ]
                )
                
                plan = Plan(steps=[celebrity_step])
                
                # Create PlanRun
                plan_run = PlanRun(plan=plan, end_user=self.end_user)
                
                print("🧠 Portia: Creating execution agent...")
                
                # Create proper execution agent following the DefaultExecutionAgent pattern
                execution_agent = CelebrityExecutionAgent(
                    plan=plan,
                    plan_run=plan_run,
                    config=self.portia_config,
                    agent_memory=self.agent_memory,
                    end_user=self.end_user,
                    celebrity_tool=self.celebrity_tool
                )
                
                print("⚡ Portia: Executing plan...")
                
                # Execute the plan using the execution agent
                output = execution_agent.execute_sync()
                
                print("✅ Portia: Plan executed successfully")
                
                # Extract the response from the output
                if output and hasattr(output, 'result'):
                    celebrity_response = str(output.result)
                elif output and hasattr(output, 'step_outputs'):
                    celebrity_response = str(list(output.step_outputs.values())[0])
                else:
                    # Fallback if output format is unexpected
                    celebrity_response = self._simple_response_generation(user_input, {"mood": "neutral"})
                    
            except Exception as e:
                print(f"⚠️  Portia execution failed: {str(e)}")
                print("� Using direct Gemini fallback")
                celebrity_response = self._simple_response_generation(user_input, {"mood": "neutral"})
        else:
            # Direct Gemini fallback
            celebrity_response = self._simple_response_generation(user_input, {"mood": "neutral"})
        
        # Add response to history with the LOCKED celebrity name (prevents mixing)
        self.conversation_history.append(f"{response_celebrity_name}: {celebrity_response}")
        
        return celebrity_response
    
    def get_last_response_celebrity_name(self) -> str:
        """Get the celebrity name from the last response in conversation history"""
        if not self.conversation_history:
            return self.celebrities[self.current_celebrity]['name']
        
        # Look at the last entry that's a celebrity response
        for entry in reversed(self.conversation_history):
            if entry.startswith(tuple(celeb['name'] + ':' for celeb in self.celebrities.values())):
                # Extract the celebrity name before the colon
                return entry.split(':')[0].strip()
        
        # Fallback to current celebrity
        return self.celebrities[self.current_celebrity]['name']
    
    def speak_text(self, text):
        """Generate and play TTS audio"""
        if not self.tts_available or not self.audio_available:
            print("🔊 Text only (TTS or audio not available)")
            return False
            
        try:
            celeb = self.celebrities[self.current_celebrity]
            voice_config = celeb["voice"]
            
            # Create TTS request
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_config["language_code"],
                name=voice_config["name"]
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=voice_config["speaking_rate"]
            )
            
            print("🎵 Generating speech...")
            
            # Generate speech
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save to temporary file and play
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(response.audio_content)
                temp_path = temp_file.name
            
            print("🔊 Playing audio...")
            
            # Try paplay first, then aplay as fallback
            play_result = None
            try:
                play_result = subprocess.run(
                    ['paplay', temp_path],
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                try:
                    play_result = subprocess.run(
                        ['aplay', temp_path],
                        capture_output=True,
                        text=True
                    )
                except FileNotFoundError:
                    print("❌ No audio player found (paplay or aplay)")
                    return False
            
            # Clean up
            os.unlink(temp_path)
            
            if play_result and play_result.returncode == 0:
                print("✅ Audio played successfully")
                return True
            else:
                error_msg = play_result.stderr if play_result else "Unknown error"
                print(f"❌ Audio playback failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ TTS error: {str(e)}")
            return False

def main():
    """Main function with Portia SDK integration"""
    print("🎭🔊 Celebrity Companion AI - Portia SDK Multi-Agent Edition")
    print("=" * 60)
    
    ai = CelebrityCompanionAI()
    
    # Show status
    celeb_names = [info['name'] for info in ai.celebrities.values()]
    print(f"Available: {', '.join(celeb_names)}")
    print(f"🔊 Audio: {'Available' if ai.audio_available else 'Not available'}")
    print(f"🎵 TTS: {'Available' if ai.tts_available else 'Not available'}")
    print(f"🧠 Portia SDK: {'Available' if PORTIA_AVAILABLE else 'Not available'}")
    print(f"🎭 Current: {'None (will be selected based on your first message)' if ai.current_celebrity is None else ai.celebrities[ai.current_celebrity]['name']}")
    print("💬 Commands: 'quit' to exit, 'switch to [celebrity]' to change voice")
    print("   Celebrity options: scarlett, morgan, david, peter")
    print("   Additional commands: 'voices' to show voice characteristics, 'info' for celebrity details, 'logic' to see selection logic\n")
    
    # Note: No initial voice test since celebrity will be selected based on first user message
    print("💡 Start by typing your message - I'll automatically select the best celebrity for you!")
    print()
    
    # Interactive mode
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'voices':
                print("\n🎭 Voice Characteristics:")
                print("=" * 50)
                for key, celeb in ai.celebrities.items():
                    print(f"\n{celeb['name']} ({key}):")
                    print(f"  Voice: {celeb['voice_description']}")
                print("=" * 50)
                continue
            elif user_input.lower() == 'info':
                if ai.current_celebrity is None:
                    print("\n🎭 No celebrity selected yet")
                    print("=" * 40)
                    print("I'll automatically select the best celebrity based on your message.")
                    print("Try typing something to see which celebrity I choose for you!")
                    print("=" * 40)
                else:
                    current = ai.celebrities[ai.current_celebrity]
                    print(f"\n🎭 Current Celebrity: {current['name']}")
                    print("=" * 40)
                    print(f"Personality: {current['personality']}")
                    print(f"Style: {current['style']}")
                    print(f"Specialties: {', '.join(current['specialties'])}")
                    print(f"Voice: {current['voice_description']}")
                    print("=" * 40)
                continue
            elif user_input.lower() == 'logic':
                print("\n🧠 Celebrity Selection Logic:")
                print("=" * 50)
                print("I analyze your message to select the best celebrity:")
                print("\n🎭 David Attenborough:")
                print("  - Anxiety, overwhelm, stress")
                print("  - Nature wisdom and calming presence")
                print("\n🎭 Morgan Freeman:")
                print("  - Sadness, grief, loneliness, confusion")
                print("  - Deep comfort and existential wisdom")
                print("\n🎭 Scarlett Johansson:")
                print("  - Anger, frustration, relationships")
                print("  - Modern psychology and emotional validation")
                print("\n🎭 Peter Griffin:")
                print("  - Work issues, light topics")
                print("  - Relatable peer support and humor")
                print("=" * 50)
                continue
            
            if not user_input:
                continue
            
            # Generate response using Portia multi-agent system
            response = ai.chat(user_input)
            
            # Get the celebrity name that actually generated this response (prevents personality mixing)
            response_celebrity_name = ai.get_last_response_celebrity_name()
            print(f"🎬 {response_celebrity_name}: {response}")
            
            # Handle switching vs normal responses
            if response.startswith('✨ Switched to') or response.startswith('❌ Celebrity not found'):
                if response.startswith('✨ Switched to'):
                    # Introduce the new celebrity with their voice
                    new_name = ai.celebrities[ai.current_celebrity]['name']
                    intro_message = f"Hello there! This is {new_name}. I'm delighted to speak with you."
                    print(f"🎬 {new_name}: {intro_message}")
                    ai.speak_text(intro_message)
            else:
                # Speak normal responses
                ai.speak_text(response)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
