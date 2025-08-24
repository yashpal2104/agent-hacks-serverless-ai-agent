#!/usr/bin/env python3
"""
📅🎭🔊 Celebrity Calendar Assistant - REAL CALENDAR WITH IMPROVED DELETE
=====================================================================
Manage your Google Calendar with celebrity voices reading your REAL events!
Now with enhanced delete functionality and action confirmations.
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

# Import Portia SDK with proper authentication
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

class CalendarCelebrityVoice:
    def __init__(self):
        """Initialize advanced TTS with natural voices for calendar events"""
        
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
        
    def setup_google_voices(self):
        """Setup Google Cloud TTS voices with authentic celebrity configurations"""
        self.celebrity_voices = {
            "David Attenborough": {
                'language_code': 'en-GB',
                'name': 'en-GB-Journey-D',
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 0.8,
                'pitch': 0.0,  # Premium Journey voices don't support pitch
                'voice_description': "Speak with a gentle, breathy, and awe-inspired tone. Use a refined British accent, soft and curious, as though narrating a nature documentary about your daily schedule."
            },
            "Morgan Freeman": {
                'language_code': 'en-US',
                'name': 'en-US-Journey-D',
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 0.75,
                'pitch': 0.0,  # Premium Journey voices don't support pitch - use natural deep voice
                'voice_description': "Speak with a deep, steady, and resonant tone. Pause often for dramatic effect. Deliver calendar information as though you are narrating something profound about time and appointments."
            },
            "Scarlett Johansson": {
                'language_code': 'en-US',
                'name': 'en-US-Journey-F',
                'gender': texttospeech.SsmlVoiceGender.FEMALE,
                'speaking_rate': 0.9,
                'pitch': 0.0,  # Premium Journey voices don't support pitch
                'voice_description': "Speak in a smooth, slightly husky and modern voice. Keep your pace gentle, with a calm confidence. Add warmth when discussing calendar events."
            },
            "Peter Griffin": {
                'language_code': 'en-US',
                'name': 'en-US-Casual-K',
                'gender': texttospeech.SsmlVoiceGender.MALE,
                'speaking_rate': 1.1,
                'pitch': 0.0,  # Use safer pitch value for Casual voice
                'voice_description': "Speak with Peter Griffin's characteristic enthusiasm about calendar events and meetings."
            }
        }
    
    def setup_local_voices(self):
        """Setup local voices with better settings"""
        voices = self.engine.getProperty('voices')
        english_voices = [v for v in voices if 'english' in v.name.lower() or 'en-' in v.id.lower()]
        
        print(f"🔍 Found {len(english_voices)} English voices")
        self.english_voices = english_voices
        
        self.celebrity_configs = {
            "David Attenborough": {'rate': 160, 'volume': 0.9, 'voice_idx': 0},
            "Morgan Freeman": {'rate': 145, 'volume': 0.95, 'voice_idx': 1},
            "Scarlett Johansson": {'rate': 170, 'volume': 0.85, 'voice_idx': 2},
            "Peter Griffin": {'rate': 190, 'volume': 1.0, 'voice_idx': 0}
        }
    
    def generate_google_speech(self, text, celebrity_name):
        """Generate speech using Google Cloud TTS"""
        voice_config = self.celebrity_voices[celebrity_name]
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name'],
            ssml_gender=voice_config['gender']
        )
        
        # Create audio config - some voices don't support pitch
        audio_config_params = {
            'audio_encoding': texttospeech.AudioEncoding.MP3,
            'speaking_rate': voice_config['speaking_rate']
        }
        
        # Only add pitch if it's not zero (some premium voices don't support pitch)
        if voice_config.get('pitch', 0) != 0:
            try:
                audio_config = texttospeech.AudioConfig(
                    pitch=voice_config['pitch'],
                    **audio_config_params
                )
            except Exception:
                # Fallback without pitch if not supported
                audio_config = texttospeech.AudioConfig(**audio_config_params)
        else:
            audio_config = texttospeech.AudioConfig(**audio_config_params)
        
        try:
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            return response.audio_content
        except Exception as e:
            # If pitch caused an error, retry without pitch
            if "pitch" in str(e).lower():
                print(f"⚠️ Retrying without pitch adjustment for {celebrity_name}")
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=voice_config['speaking_rate']
                )
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                return response.audio_content
            else:
                raise e
    
    def generate_local_speech(self, text, celebrity_name):
        """Generate speech using local TTS"""
        config = self.celebrity_configs.get(celebrity_name, self.celebrity_configs["David Attenborough"])
        
        self.engine.setProperty('rate', config['rate'])
        self.engine.setProperty('volume', config['volume'])
        
        if self.english_voices:
            voice_idx = min(config['voice_idx'], len(self.english_voices) - 1)
            selected_voice = self.english_voices[voice_idx]
            self.engine.setProperty('voice', selected_voice.id)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        self.engine.save_to_file(text, temp_path)
        self.engine.runAndWait()
        return temp_path
    
    def speak_calendar_event(self, text, celebrity_name):
        """Generate and play natural celebrity speech for calendar events"""
        print(f"🎬 {celebrity_name} is preparing to speak about your calendar...")
        
        try:
            if self.use_google_tts:
                print("🎙️ Generating with Google's premium natural voice...")
                audio_content = self.generate_google_speech(text, celebrity_name)
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(audio_content)
                temp_file.close()
                
                print(f"🔊 {celebrity_name} is speaking about your calendar!")
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                os.unlink(temp_file.name)
            else:
                print("🎤 Generating with improved local voice...")
                audio_path = self.generate_local_speech(text, celebrity_name)
                
                print(f"🔊 {celebrity_name} is speaking!")
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                os.unlink(audio_path)
            
            print(f"✅ {celebrity_name} finished speaking about your calendar!")
            
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
            print(f"\n🗣️ {celebrity_name} says:")
            print("─" * 40)
            print(text)
            print("─" * 40)

def init_portia_calendar():
    """Initialize Portia with proper authentication for calendar access - Gmail Success Approach"""
    try:
        print("🔧 Setting up Portia with working configuration...")
        
        # Use the same successful config approach as Gmail
        config = default_config()
        
        # Configure working Claude model to avoid 404 errors (same as Gmail)
        working_model = "anthropic/claude-3-5-haiku-20241022"
        config.models.default_model = working_model
        config.models.planning_model = working_model
        config.models.execution_model = working_model
        config.models.introspection_model = working_model
        
        # Create Portia instance with working config
        portia = Portia(tools=PortiaToolRegistry(config), config=config)
        print("✅ Portia configured with working Claude model and Google Calendar tools")
        
        return portia
        
    except Exception as e:
        print(f"❌ Error initializing Portia: {e}")
        return None

def handle_portia_authentication(portia, initial_query="Access my Google Calendar"):
    """Handle Portia authentication flow including OAuth"""
    try:
        print(f"🔐 Setting up calendar access with query: '{initial_query}'")
        
        # Generate the plan from the user query
        plan = portia.plan(initial_query)
        print("📋 Calendar access plan created")
        
        # Run the plan
        plan_run = portia.run_plan(plan)
        
        # Handle authentication clarifications
        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            print("🔐 Authentication required for Google Calendar access...")
            
            # If clarifications are needed, resolve them before resuming the plan run
            for clarification in plan_run.get_outstanding_clarifications():
                
                # Handle Input and Multiple Choice clarifications
                if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                    print(f"ℹ️  {clarification.user_guidance}")
                    
                    options_text = ""
                    if hasattr(clarification, 'options') and clarification.options:
                        options_text = f"\nOptions:\n" + "\n".join(clarification.options) + "\n"
                    
                    user_input = input(f"Please enter a value:\n{options_text}")
                    plan_run = portia.resolve_clarification(clarification, user_input, plan_run)
                
                # Handle Action clarifications (OAuth authentication)
                elif isinstance(clarification, ActionClarification):
                    print(f"🔗 {clarification.user_guidance}")
                    print("📱 Please click on the authentication link below to proceed:")
                    print(f"🌐 {clarification.action_url}")
                    print("\n⏳ Waiting for you to complete authentication in your browser...")
                    
                    # Wait for user to complete OAuth flow
                    plan_run = portia.wait_for_ready(plan_run)
                    print("✅ Authentication completed!")
            
            # Once clarifications are resolved, resume the plan run
            plan_run = portia.resume(plan_run)
        
        print("🎉 Google Calendar authentication successful!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

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

def execute_calendar_action_with_portia(portia, action, details=""):
    """Execute calendar actions using Portia with real Google Calendar - Enhanced Delete Support"""
    try:
        # Create specific tasks for real calendar operations with improved delete functionality
        calendar_tasks = {
            "get events": f"Search my Google Calendar and get all my upcoming events and meetings for the next week. Show me the event titles, dates, times, locations, and any important details. If I have no events, say 'No events found'.",
            "check availability": f"Check my Google Calendar availability for today and the next few days. Show me my free time slots and when I'm busy with meetings or events.",
            "create event": f"Create a new event in my Google Calendar with these details: '{details}'. Set it for an appropriate time and confirm what event was created with the exact title, date, and time.",
            "delete event": f"Find and delete the event named '{details}' or containing '{details}' from my Google Calendar. First search for events matching this name or description, then delete the matching event. After deletion, confirm exactly which event was removed including the title, date, and time it was originally scheduled for.",
            "today events": f"What events do I have today (August 24, 2025) on my Google Calendar? Show me all scheduled meetings and appointments for today specifically with titles, times, and details.",
            "tomorrow events": f"What events do I have tomorrow (August 25, 2025) on my Google Calendar? Show me all scheduled meetings and appointments for tomorrow specifically with titles, times, and details."
        }
        
        # Use the task description for this action
        task = calendar_tasks.get(action, f"Help me with my Google Calendar: {action} {details}")
        
        print(f"📅 Executing real calendar task: {action}")
        print(f"🎯 Task: {task}")
        
        # Use task-based approach (like successful Gmail) - NOT plan-based
        plan_run = portia.run(task)
        
        # Handle clarifications (all types) - same as Gmail
        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
            print("\nPlease resolve the following clarifications to continue")
            for clarification in plan_run.get_outstanding_clarifications():
                # Action clarifications
                if isinstance(clarification, ActionClarification):
                    print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
                    print(clarification.action_url)
                    input("Press Enter after completing the action...")
                
                # Input clarifications  
                elif isinstance(clarification, InputClarification):
                    user_input_clarify = input(f"{clarification.prompt}: ")
                    clarification.respond(user_input_clarify)
                
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
        
        print(f"📊 Calendar task status: {plan_run.state}")
        
        # Extract calendar content from task result - USING SUCCESSFUL GMAIL APPROACH
        calendar_content = ""
        if hasattr(plan_run, 'result') and plan_run.result:
            calendar_content = str(plan_run.result)
            print(f"✅ Using plan_run.result: {calendar_content[:100]}...")
        elif hasattr(plan_run, 'outputs') and plan_run.outputs:
            calendar_content = str(plan_run.outputs)
            print(f"✅ Using plan_run.outputs: {calendar_content[:100]}...")
        
        # Fallback: extract from plan_run data (where the real data is!)
        if not calendar_content:
            plan_data = str(plan_run)
            # Look for calendar-related keywords in the plan_run string
            if any(keyword in plan_data.lower() for keyword in ['calendar', 'event', 'meeting', 'appointment', 'zoom', 'google meet', 'deleted', 'created']):
                calendar_content = plan_data
                print(f"✅ Using full plan_run data (contains real calendar info): {calendar_content[:100]}...")
        
        # Debug: Print the actual calendar content received
        print(f"📋 Final calendar content for celebrity:")
        print(f"Content length: {len(calendar_content)}")
        if len(calendar_content) > 200:
            print(f"Content preview: {calendar_content[:200]}...")
        else:
            print(f"Full content: {calendar_content}")
        
        # Check if we got meaningful calendar data
        if calendar_content and len(calendar_content.strip()) > 50:
            print("✅ Calendar content retrieved successfully!")
            return calendar_content
        else:
            print("📅 No calendar content found or content too short")
            return f"Calendar action '{action}' was completed, but no detailed information was returned."
            
    except Exception as e:
        error_msg = f"Sorry, I encountered an error while accessing your Google Calendar: {str(e)}"
        print(f"❌ Error executing calendar task: {error_msg}")
        return error_msg

def generate_calendar_script(voice_model, celebrity_name, calendar_action, calendar_content, voice_engine=None):
    """Generate natural celebrity conversation script for REAL calendar events - Enhanced Delete Confirmations"""
    
    # Debug: Print what we're actually receiving
    print(f"🔍 DEBUG - Calendar script generation:")
    print(f"Action: {calendar_action}")
    print(f"Content received: {calendar_content[:200]}..." if len(calendar_content) > 200 else f"Content: {calendar_content}")
    print(f"Content length: {len(calendar_content)}")
    
    # Get voice description if available
    voice_description = ""
    if voice_engine and hasattr(voice_engine, 'celebrity_voices') and celebrity_name in voice_engine.celebrity_voices:
        voice_info = voice_engine.celebrity_voices[celebrity_name]
        voice_description = voice_info.get('voice_description', '')
    
    calendar_prompts = {
        "David Attenborough": f"""You are David Attenborough. {voice_description}

The user performed this calendar action: {calendar_action}

Here is their REAL Google Calendar data (DO NOT make up any events, ONLY use this exact data): 
{calendar_content}

Important instructions:
- If this is a "create event" action, announce: "I've successfully created your new event: [exact event name] scheduled for [date and time]"
- If this is a "delete event" action, announce: "I've successfully deleted the event: [exact event name] that was scheduled for [date and time]"
- If this is "get events", read their actual upcoming events with fascination. If no events, say so clearly.
- ONLY mention events that are in the real calendar data above. Never invent fake events.
- Be specific about dates, times, and event names when confirming actions.
- End by offering help: "If you need anything just ask, I will help you."

Be conversational but ONLY talk about their real events and actions.""",
        
        "Morgan Freeman": f"""You are Morgan Freeman. {voice_description}

The user performed this calendar action: {calendar_action}

Here is their REAL Google Calendar data (DO NOT make up any events, ONLY use this exact data):
{calendar_content}

Important instructions:
- If this is a "create event" action, confirm: "I have successfully created your new event: [exact event name] for [date and time]"
- If this is a "delete event" action, confirm: "I have successfully removed the event: [exact event name] that was scheduled for [date and time]"
- If this is "get events", speak about their actual upcoming events with wisdom. If no events, state that clearly.
- ONLY mention the real events that are in their calendar data above. Do not invent any fake meetings.
- Be specific about event details when confirming create/delete actions.
- End by offering help: "If you need anything just ask, I will help you."

Only discuss their real schedule with thoughtful perspective.""",
        
        "Scarlett Johansson": f"""You are Scarlett Johansson. {voice_description}

The user performed this calendar action: {calendar_action}

Here is their REAL Google Calendar data (DO NOT make up any events, ONLY use this exact data):
{calendar_content}

Important instructions:
- If this is a "create event" action, confidently announce: "I've created your new event: [exact event name] scheduled for [date and time]"
- If this is a "delete event" action, confidently confirm: "I've successfully deleted the event: [exact event name] that was scheduled for [date and time]"
- If this is "get events", discuss their actual upcoming events with warmth. If no events, say so clearly.
- ONLY mention the real events from their calendar data above. Never create fake events.
- Be specific and clear about event names, dates, and times when confirming actions.
- End by offering help: "If you need anything just ask, I will help you."

Be engaging about their real appointments only.""",
        
        "Peter Griffin": f"""You are Peter Griffin. {voice_description}

The user performed this calendar action: {calendar_action}

Here is their REAL Google Calendar data (DO NOT make up any events, ONLY use this exact data):
{calendar_content}

Important instructions:
- If this is a "create event" action, react excitedly: "Sweet! I created your event: [exact event name] for [date and time]!"
- If this is a "delete event" action, react with enthusiasm: "Boom! Deleted that event: [exact event name] that was on [date and time]!"
- If this is "get events", talk about their real upcoming events in Peter style. If no events, mention that.
- ONLY mention the real events from their calendar data above. Don't make up fake stuff.
- Be specific about the event details when confirming what was done.
- End by offering help: "If you need anything just ask, I will help you."

React to their real appointments only, no fake events."""
    }
    
    prompt = calendar_prompts.get(celebrity_name, calendar_prompts["David Attenborough"])
    
    if voice_model:
        try:
            response = voice_model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Script generation error: {e}")
    
    # Fallback script with real data only
    return f"Hi there! This is {celebrity_name}. Here are your real calendar events: {calendar_content} If you need anything just ask, I will help you."

def main():
    print("📅🎭🔊 CELEBRITY CALENDAR ASSISTANT - REAL CALENDAR")
    print("=" * 52)
    print("Manage your Google Calendar with celebrity voices reading your REAL events!")
    print("🗑️ Enhanced delete functionality with confirmations!")
    print()
    
    # Setup components
    content_model = setup_content_generator()
    voice_engine = CalendarCelebrityVoice()
    
    # Initialize Portia for real calendar access
    print("🔧 Connecting to Google Calendar via Portia...")
    portia = init_portia_calendar()
    
    if not portia:
        print("❌ Unable to initialize Portia - cannot access real calendar")
        return
    
    # Handle authentication
    print("🔐 Setting up Google Calendar authentication...")
    auth_success = handle_portia_authentication(portia)
    
    if not auth_success:
        print("❌ Authentication failed - cannot access your calendar")
        return
    
    print("✅ Successfully connected to your Google Calendar!")
    
    # Celebrity selection
    celebrities = {
        "david": "David Attenborough",
        "morgan": "Morgan Freeman", 
        "scarlett": "Scarlett Johansson",
        "peter": "Peter Griffin"
    }
    
    print("\n🎭 CELEBRITY ASSISTANT SELECTION")
    for key, name in celebrities.items():
        print(f"  {key}: {name}")
    celebrity_key = input("Choose your celebrity calendar assistant: ").strip().lower()
    
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
    
    print(f"\n🎬 {celebrity_name} is now your REAL calendar assistant!")
    
    # Main interaction loop with real calendar
    while True:
        print(f"\n📅 REAL CALENDAR ACTIONS (with {celebrity_name})")
        print("Available commands:")
        print("  • 'get events' - View your real upcoming calendar events")
        print("  • 'today events' - See what you have scheduled today")
        print("  • 'tomorrow events' - Check tomorrow's schedule")
        print("  • 'check availability' - Check when you're actually free")  
        print("  • 'create event [description]' - Create a real calendar event")
        print("  • 'delete event [event name]' - Remove a real calendar event")
        print("  • 'quit' - Exit the calendar assistant")
        
        user_request = input(f"\n🎭 What would you like {celebrity_name} to help you with? ").strip()
        
        if user_request.lower() in ['quit', 'exit', 'bye']:
            farewell_script = generate_calendar_script(
                content_model,
                celebrity_name,
                "saying goodbye",
                "Thank you for using your celebrity calendar assistant with your real Google Calendar. Have a wonderful day managing your actual schedule!",
                voice_engine
            )
            voice_engine.speak_calendar_event(farewell_script, celebrity_name)
            break
        
        # Determine calendar action and extract details - Enhanced Delete Parsing
        calendar_action = "get events"  # default
        additional_details = ""
        
        if "today" in user_request.lower():
            calendar_action = "today events"
        elif "tomorrow" in user_request.lower():
            calendar_action = "tomorrow events"
        elif user_request.lower().startswith("get events"):
            calendar_action = "get events"
        elif user_request.lower().startswith("check availab"):
            calendar_action = "check availability"
        elif user_request.lower().startswith("create event"):
            calendar_action = "create event"
            additional_details = user_request[12:].strip()  # Get description after "create event"
            if not additional_details:
                additional_details = input("📝 What event would you like to create? ").strip()
        elif user_request.lower().startswith("delete event"):
            calendar_action = "delete event"
            additional_details = user_request[12:].strip()  # Get event name after "delete event"
            if not additional_details:
                additional_details = input("🗑️ Which event would you like to delete? Enter the event name: ").strip()
        
        # If no specific details provided, try to extract from general request
        elif "create" in user_request.lower() and "event" in user_request.lower():
            calendar_action = "create event"
            additional_details = user_request.replace("create", "").replace("event", "").strip()
            if not additional_details:
                additional_details = input("📝 What event would you like to create? ").strip()
        elif "delete" in user_request.lower() and ("event" in user_request.lower() or "meeting" in user_request.lower()):
            calendar_action = "delete event"  
            additional_details = user_request.replace("delete", "").replace("event", "").replace("meeting", "").strip()
            if not additional_details:
                additional_details = input("🗑️ Which event would you like to delete? Enter the event name: ").strip()
        
        # Execute real calendar action using Portia
        print(f"📅 {celebrity_name} is accessing your real Google Calendar...")
        print(f"🎯 Action: {calendar_action}")
        if additional_details:
            print(f"📝 Details: '{additional_details}'")
        
        calendar_result = execute_calendar_action_with_portia(portia, calendar_action, additional_details)
        
        # Generate celebrity response about real calendar data
        print(f"✍️ {celebrity_name} is preparing to read your real calendar events...")
        script = generate_calendar_script(content_model, celebrity_name, calendar_action, calendar_result, voice_engine)
        
        # Deliver celebrity response about real events
        print(f"\n🎬 {celebrity_name} has your REAL calendar update:")
        voice_engine.speak_calendar_event(script, celebrity_name)

if __name__ == "__main__":
    main()
