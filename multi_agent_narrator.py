"""
Multi-Agent David Attenborough Documentary System
=================================================
Multiple AI agents with different personalities working together to create rich documentary commentary.
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

from portia import (
    Portia, Config, StorageClass, LogLevel,
    PlanBuilderV2, StepOutput, Input,
    Tool, ToolRunContext, ToolHardError,
    MultipleChoiceClarification
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
# CUSTOM PORTIA TOOLS WITH CLARIFICATIONS
# =====================================

class ImageAnalysisToolSchema(BaseModel):
    """Schema for image analysis tool."""
    image_path: str = Field(..., description="Path to the image file to analyze")
    analysis_focus: str = Field(default="general", description="Focus area: general, facial, environmental, behavioral")

class ImageAnalysisTool(Tool[Dict[str, Any]]):
    """Custom tool for detailed image analysis with clarifications."""
    
    id: str = "image_analysis_tool"
    name: str = "Image Analysis Tool"
    description: str = "Analyzes images for documentary purposes with multiple focus options"
    args_schema: type[BaseModel] = ImageAnalysisToolSchema
    output_schema: tuple[str, str] = ("dict", "Detailed analysis results")

    def run(self, ctx: ToolRunContext, image_path: str, analysis_focus: str = "general") -> Dict[str, Any] | MultipleChoiceClarification:
        """Run image analysis with clarifications for missing files."""
        
        file_path = Path(image_path)
        
        # Check if file exists
        if not file_path.exists():
            # Look for alternative image files
            alt_paths = self.find_image_files()
            if alt_paths:
                return MultipleChoiceClarification(
                    plan_run_id=ctx.plan_run.id,
                    argument_name="image_path",
                    user_guidance=f"Image not found at {image_path}. Found these alternatives:",
                    options=alt_paths,
                )
            raise ToolHardError(f"No image found at {image_path}")
        
        # Perform analysis
        try:
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Convert to PIL Image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Generate analysis based on focus
            analysis_prompts = {
                "general": "Analyze this image comprehensively for documentary narration",
                "facial": "Focus on facial expressions, micro-expressions, and emotional cues",
                "environmental": "Analyze the environment, lighting, background, and setting",
                "behavioral": "Focus on body language, posture, and behavioral indicators"
            }
            
            prompt = analysis_prompts.get(analysis_focus, analysis_prompts["general"])
            response = model.generate_content([prompt, image])
            
            return {
                "analysis": response.text,
                "focus": analysis_focus,
                "image_path": str(file_path),
                "timestamp": time.time()
            }
            
        except Exception as e:
            raise ToolHardError(f"Analysis failed: {str(e)}")

    def find_image_files(self) -> List[str]:
        """Find alternative image files."""
        search_paths = [Path("frames"), Path("."), Path("images")]
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        found_files = []
        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.iterdir():
                    if file_path.suffix.lower() in image_extensions:
                        found_files.append(str(file_path))
        
        return found_files[:5]  # Limit to 5 options

class NarrationHistoryToolSchema(BaseModel):
    """Schema for narration history tool."""
    agent_name: str = Field(..., description="Name of the agent whose history to retrieve")
    limit: int = Field(default=3, description="Number of recent narrations to retrieve")

class NarrationHistoryTool(Tool[List[Dict[str, Any]]]):
    """Tool to manage and retrieve agent narration history."""
    
    id: str = "narration_history_tool"
    name: str = "Narration History Tool"
    description: str = "Retrieves and manages narration history for different agents"
    args_schema: type[BaseModel] = NarrationHistoryToolSchema
    output_schema: tuple[str, str] = ("list", "List of previous narrations")

    def __init__(self):
        super().__init__()
        self.history_file = Path("agent_history.json")
        self.history: Dict[str, List[Dict[str, Any]]] = self.load_history()

    def run(self, ctx: ToolRunContext, agent_name: str, limit: int = 3) -> List[Dict[str, Any]] | MultipleChoiceClarification:
        """Get narration history for an agent."""
        
        if agent_name not in self.history:
            # Offer available agents if the requested one doesn't exist
            available_agents = list(self.history.keys())
            if available_agents:
                return MultipleChoiceClarification(
                    plan_run_id=ctx.plan_run.id,
                    argument_name="agent_name",
                    user_guidance=f"Agent '{agent_name}' not found. Available agents:",
                    options=available_agents,
                )
            return []
        
        return self.history[agent_name][-limit:] if limit > 0 else self.history[agent_name]

    def add_narration(self, agent_name: str, narration: str, metadata: Dict[str, Any] = None):
        """Add a new narration to history."""
        if agent_name not in self.history:
            self.history[agent_name] = []
        
        entry = {
            "narration": narration,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.history[agent_name].append(entry)
        self.save_history()

    def load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")

# =====================================
# MULTI-AGENT PERSONALITY DEFINITIONS
# =====================================

class AgentPersonality:
    """Base class for agent personalities."""
    
    def __init__(self, name: str, voice_settings: Dict[str, Any], specialty: str):
        self.name = name
        self.voice_settings = voice_settings
        self.specialty = specialty
        self.history = []

class DavidAttenboroughAgent(AgentPersonality):
    """Main narrator - David Attenborough personality."""
    
    def __init__(self):
        super().__init__(
            name="David Attenborough",
            voice_settings={
                "language_code": "en-GB",
                "name": "en-GB-Neural2-B",
                "speaking_rate": 0.85,
                "pitch": -3.0
            },
            specialty="Primary documentary narration with conversational warmth"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are Sir David Attenborough in a casual, conversational mood. You're observing human behavior like you would animals in nature, but with warmth and curiosity.

YOUR CONVERSATIONAL STYLE:
- Use contractions: "don't", "can't", "that's", "I'm", "you're"
- Natural words: "well," "you know," "quite," "rather," "indeed"
- Add gentle pauses: "..." and natural flow
- Show genuine fascination with tiny details
- Maintain that signature British charm but relaxed
- Still refer to them as "Homo sapiens" occasionally

{context}

Observe with wonder and share your genuine curiosity about human behavior."""

class WildlifeExpertAgent(AgentPersonality):
    """Supporting agent focused on behavioral analysis."""
    
    def __init__(self):
        super().__init__(
            name="Wildlife Expert",
            voice_settings={
                "language_code": "en-GB", 
                "name": "en-GB-Neural2-A",
                "speaking_rate": 0.9,
                "pitch": -1.0
            },
            specialty="Behavioral analysis and evolutionary insights"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are a wildlife behavioral expert working with David Attenborough. Focus on the scientific and evolutionary aspects of human behavior you observe.

YOUR STYLE:
- More analytical than David, but still conversational
- Draw parallels to animal behavior
- Use scientific terminology naturally
- Explain evolutionary advantages
- Support David's observations with deeper insights

{context}

Provide scientific depth to the observations."""

class CinematographerAgent(AgentPersonality):
    """Agent focused on visual and technical aspects."""
    
    def __init__(self):
        super().__init__(
            name="Cinematographer", 
            voice_settings={
                "language_code": "en-US",
                "name": "en-US-Neural2-J", 
                "speaking_rate": 1.0,
                "pitch": 0.0
            },
            specialty="Visual composition, lighting, and technical observation"
        )

    def get_prompt(self, context: str = "") -> str:
        return f"""You are an experienced documentary cinematographer working with the team. Focus on the visual and technical aspects of what you're observing.

YOUR EXPERTISE:
- Lighting quality and its effects
- Composition and visual elements
- Color theory and mood
- Technical aspects of the scene
- How visuals support the story

{context}

Provide insights about the visual storytelling elements."""

# =====================================
# MULTI-AGENT ORCHESTRATION SYSTEM
# =====================================

class MultiAgentDocumentarySystem:
    """Orchestrates multiple AI agents for rich documentary creation."""
    
    def __init__(self):
        # Initialize agents
        self.agents = {
            "david": DavidAttenboroughAgent(),
            "expert": WildlifeExpertAgent(), 
            "cinematographer": CinematographerAgent()
        }
        
        # Initialize custom tools
        self.image_tool = ImageAnalysisTool()
        self.history_tool = NarrationHistoryTool()
        
        # Create custom tool registry
        self.custom_tools = [self.image_tool, self.history_tool] + list(example_tool_registry.values())
        
        # Initialize Portia
        self.config = Config.from_default(
            storage_class=StorageClass.DISK,
            storage_dir='multi_agent_runs',
            default_log_level=LogLevel.DEBUG
        )
        
        self.portia = Portia(config=self.config, tools=self.custom_tools)
        
    def create_multi_agent_plan(self):
        """Create a sophisticated multi-agent analysis plan."""
        
        plan = (
            PlanBuilderV2()
            .input(name="image_path", description="Path to the image to analyze")
            .input(name="session_count", description="Current session number", default_value=1)
            
            # Step 1: Detailed Image Analysis
            .tool_step(
                tool_id="image_analysis_tool",
                inputs={
                    "image_path": Input("image_path"),
                    "analysis_focus": "general"
                },
                step_name="image_analysis"
            )
            
            # Step 2: Get David's previous narrations for context
            .tool_step(
                tool_id="narration_history_tool", 
                inputs={
                    "agent_name": "David Attenborough",
                    "limit": 2
                },
                step_name="david_history"
            )
            
            # Step 3: David's Primary Narration
            .llm_step(
                task="""You are Sir David Attenborough providing conversational documentary narration.

Image Analysis: {{image_analysis}}
Your Recent Comments: {{david_history}}
Session: {{session_count}}

Create natural, conversational narration with contractions, genuine curiosity, and that signature warmth. Don't repeat previous observations - find something new and fascinating.""",
                inputs=[StepOutput("image_analysis"), StepOutput("david_history"), Input("session_count")],
                step_name="david_narration"
            )
            
            # Step 4: Wildlife Expert's Behavioral Analysis  
            .llm_step(
                task="""You are a wildlife behavioral expert adding scientific depth to David's observation.

Image Analysis: {{image_analysis}}
David's Narration: {{david_narration}}

Provide behavioral insights, evolutionary context, or scientific explanations that complement David's observations. Keep it conversational but scientifically informed.""",
                inputs=[StepOutput("image_analysis"), StepOutput("david_narration")],
                step_name="expert_analysis"
            )
            
            # Step 5: Cinematographer's Visual Insights
            .llm_step(
                task="""You are a documentary cinematographer commenting on the visual aspects.

Image Analysis: {{image_analysis}}
David's Narration: {{david_narration}}

Focus on lighting, composition, visual mood, and how the technical aspects support the documentary narrative. Keep it brief but insightful.""",
                inputs=[StepOutput("image_analysis"), StepOutput("david_narration")],
                step_name="visual_analysis"
            )
            
            # Step 6: Synthesize Multi-Agent Output
            .llm_step(
                task="""Combine the multi-agent observations into a rich, layered documentary segment.

David's Narration: {{david_narration}}
Expert Analysis: {{expert_analysis}}
Visual Insights: {{visual_analysis}}

Create a natural flow that weaves together all perspectives into engaging documentary commentary.""",
                inputs=[
                    StepOutput("david_narration"),
                    StepOutput("expert_analysis"), 
                    StepOutput("visual_analysis")
                ],
                step_name="final_synthesis"
            )
            
            .final_output(StepOutput("final_synthesis"))
            .build()
        )
        
        return plan

    def generate_audio(self, text: str, agent: AgentPersonality):
        """Generate TTS audio for specific agent."""
        if not TTS_AVAILABLE:
            print(f"🎙️ {agent.name}: {text}")
            return None
            
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=agent.voice_settings["language_code"],
                name=agent.voice_settings["name"],
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=agent.voice_settings["speaking_rate"],
                pitch=agent.voice_settings["pitch"],
            )
            
            response = tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save audio file
            timestamp = int(time.time())
            dir_path = Path(f"multi_agent_audio/{agent.name.lower().replace(' ', '_')}")
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / f"{timestamp}.wav"
            
            with open(file_path, "wb") as out:
                out.write(response.audio_content)
            
            print(f"🎵 {agent.name} audio saved: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"⚠️ TTS error for {agent.name}: {e}")
            return None

    async def run_multi_agent_analysis(self, image_path: str, session_count: int):
        """Run the multi-agent documentary analysis."""
        
        try:
            print(f"🎬 Running multi-agent analysis (Session {session_count})")
            
            # Create and execute plan
            plan = self.create_multi_agent_plan()
            
            result = await self.portia.run_async(
                plan_definition=plan,
                inputs={
                    "image_path": image_path,
                    "session_count": session_count
                }
            )
            
            if result and hasattr(result, 'output'):
                final_commentary = result.output
                print("✅ Multi-agent analysis complete!")
                
                # Save to history
                self.history_tool.add_narration(
                    "Multi-Agent System",
                    final_commentary,
                    {"session": session_count, "agents": list(self.agents.keys())}
                )
                
                return final_commentary
            else:
                return "Multi-agent analysis completed but no output received."
                
        except Exception as e:
            print(f"❌ Multi-agent analysis error: {e}")
            return f"Analysis error: {str(e)}"

# =====================================
# MAIN EXECUTION
# =====================================

async def main():
    """Main multi-agent documentary system."""
    
    system = MultiAgentDocumentarySystem()
    session_count = 0
    
    print("🎬 MULTI-AGENT DOCUMENTARY SYSTEM")
    print("👥 Featuring: David Attenborough, Wildlife Expert, Cinematographer")
    print("🛠️ Enhanced with Custom Portia Tools & Clarifications")
    print("🎙️ Individual TTS voices for each agent")
    print("-" * 70)
    
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
            print(f"\n🎥 SESSION {session_count}")
            print("=" * 50)
            
            # Run multi-agent analysis
            commentary = await system.run_multi_agent_analysis(image_path, session_count)
            
            print(f"\n🎭 MULTI-AGENT DOCUMENTARY COMMENTARY:")
            print("-" * 50)
            print(commentary)
            print("-" * 50)
            
            # Generate audio for David (primary narrator)
            david_agent = system.agents["david"]
            audio_file = system.generate_audio(commentary[:500], david_agent)
            
            print(f"\n⏳ Waiting 30 seconds before next multi-agent session...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🎬 Multi-agent documentary session ended. All agents signing off!")
            break
        except Exception as e:
            print(f"❌ Session error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    print("🎬 MULTI-AGENT DAVID ATTENBOROUGH DOCUMENTARY SYSTEM")
    print("👥 Multiple AI Personalities | Custom Portia Tools | Clarifications")
    print("=" * 70)
    asyncio.run(main())
