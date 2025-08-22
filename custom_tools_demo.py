"""
Custom Portia Tools Demo with Clarifications
===========================================
Demonstrates custom tools with MultipleChoiceClarification capabilities
"""

import asyncio
from pathlib import Path
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from portia import (
    Portia, Config, StorageClass,
    PlanBuilderV2, StepOutput, Input,
    Tool, ToolRunContext, ToolHardError,
    MultipleChoiceClarification
)

# =====================================
# CUSTOM TOOLS WITH CLARIFICATIONS
# =====================================

class FileReaderToolSchema(BaseModel):
    """Schema for file reader tool."""
    filename: str = Field(..., description="The location where the file should be read from")

class FileReaderTool(Tool[str]):
    """Finds and reads content from a local file with clarification support."""
    
    id: str = "file_reader_tool"
    name: str = "File Reader Tool"
    description: str = "Finds and reads content from a local file on disk"
    args_schema: type[BaseModel] = FileReaderToolSchema
    output_schema: tuple[str, str] = ("str", "A string dump or JSON of the file content")

    def run(self, ctx: ToolRunContext, filename: str) -> str | Dict[str, Any] | MultipleChoiceClarification:
        """Run the FileReaderTool with clarification support."""
        
        file_path = Path(filename)
        suffix = file_path.suffix.lower()

        if file_path.is_file():
            # File exists, read it
            try:
                if suffix == '.json':
                    with file_path.open('r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        return json.dumps(data, indent=2)
                elif suffix in ['.txt', '.log', '.md', '.py']:
                    return file_path.read_text(encoding="utf-8")
                else:
                    return f"File found but format {suffix} not fully supported. Raw content: {file_path.read_text(encoding='utf-8')[:500]}..."
            except Exception as e:
                raise ToolHardError(f"Error reading file: {str(e)}")
        
        # File not found, look for alternatives
        alt_file_paths = self.find_file(filename)
        if alt_file_paths:
            return MultipleChoiceClarification(
                plan_run_id=ctx.plan_run.id,
                argument_name="filename",
                user_guidance=f"File '{filename}' not found. Found these alternatives:",
                options=alt_file_paths,
            )

        raise ToolHardError(f"No file found with the name '{filename}' in the project directory.")

    def find_file(self, filename: str) -> List[str]:
        """Find alternative file locations."""
        search_path = Path(".")
        filepaths = []
        
        # Search for exact filename
        for filepath in search_path.rglob(filename):
            if filepath.is_file():
                filepaths.append(str(filepath))
        
        # If no exact matches, search for similar filenames
        if not filepaths:
            file_stem = Path(filename).stem
            for filepath in search_path.rglob(f"{file_stem}*"):
                if filepath.is_file():
                    filepaths.append(str(filepath))
        
        return filepaths[:5]  # Limit to 5 options

class NarratorConfigToolSchema(BaseModel):
    """Schema for narrator configuration tool."""
    narrator_type: str = Field(..., description="Type of narrator: david, expert, cinematographer, or multi")
    voice_speed: float = Field(default=0.85, description="Speaking speed (0.5-2.0)")

class NarratorConfigTool(Tool[Dict[str, Any]]):
    """Tool for configuring narrator settings with clarifications."""
    
    id: str = "narrator_config_tool"
    name: str = "Narrator Config Tool"
    description: str = "Configures narrator settings and voice parameters"
    args_schema: type[BaseModel] = NarratorConfigToolSchema
    output_schema: tuple[str, str] = ("dict", "Configuration settings")

    def run(self, ctx: ToolRunContext, narrator_type: str, voice_speed: float = 0.85) -> Dict[str, Any] | MultipleChoiceClarification:
        """Configure narrator with clarifications for invalid options."""
        
        valid_types = ["david", "expert", "cinematographer", "multi"]
        
        if narrator_type.lower() not in valid_types:
            return MultipleChoiceClarification(
                plan_run_id=ctx.plan_run.id,
                argument_name="narrator_type",
                user_guidance=f"'{narrator_type}' is not a valid narrator type. Please choose:",
                options=valid_types,
            )
        
        # Validate voice speed
        if not 0.5 <= voice_speed <= 2.0:
            voice_speed = max(0.5, min(2.0, voice_speed))  # Clamp to valid range
        
        config = {
            "narrator_type": narrator_type.lower(),
            "voice_speed": voice_speed,
            "voice_settings": self.get_voice_settings(narrator_type.lower()),
            "timestamp": "2025-08-21"
        }
        
        return config

    def get_voice_settings(self, narrator_type: str) -> Dict[str, Any]:
        """Get voice settings for narrator type."""
        settings = {
            "david": {"language": "en-GB", "name": "en-GB-Neural2-B", "pitch": -3.0},
            "expert": {"language": "en-GB", "name": "en-GB-Neural2-A", "pitch": -1.0},
            "cinematographer": {"language": "en-US", "name": "en-US-Neural2-J", "pitch": 0.0},
            "multi": {"language": "en-GB", "name": "en-GB-Neural2-B", "pitch": -2.0}
        }
        return settings.get(narrator_type, settings["david"])

# =====================================
# DEMO PLAN WITH CUSTOM TOOLS
# =====================================

def demo_custom_tools():
    """Demonstrate custom tools with clarifications."""
    
    # Initialize Portia with custom tools
    config = Config.from_default(
        storage_class=StorageClass.DISK,
        storage_dir='demo_custom_tools'
    )
    
    custom_tools = [FileReaderTool(), NarratorConfigTool()]
    portia = Portia(config=config, tools=custom_tools)
    
    # Create demo plan
    plan = (
        PlanBuilderV2()
        .input(name="config_file", description="Configuration file to read", default_value="narrator_config.json")
        .input(name="narrator_choice", description="Preferred narrator", default_value="david")
        
        # Step 1: Try to read configuration file (will trigger clarification if not found)
        .llm_step(
            task="""Try to read and analyze a configuration file. If the file doesn't exist, suggest alternatives.

Config file requested: {{config_file}}

Provide a configuration analysis or suggest what a good narrator configuration should contain.""",
            inputs=[Input("config_file")],
            step_name="read_config"
        )
        
        # Step 2: Configure narrator settings
        .llm_step(
            task="""Configure narrator settings based on the choice and any config file information.

Narrator choice: {{narrator_choice}}
Config info: {{read_config}}

Create appropriate narrator settings for documentary narration. Include voice settings, personality traits, and speaking style.""",
            inputs=[Input("narrator_choice"), StepOutput("read_config")],
            step_name="setup_narrator"
        )
        
        # Step 3: Generate summary
        .llm_step(
            task="""Based on the configuration and narrator setup, create a brief summary:

Configuration Analysis: {{read_config}}
Narrator Settings: {{setup_narrator}}

Provide a summary of the documentary narrator system configuration.""",
            inputs=[StepOutput("read_config"), StepOutput("setup_narrator")],
            step_name="configuration_summary"
        )
        
        .final_output(StepOutput("configuration_summary"))
        .build()
    )
    
    print("🛠️ CUSTOM TOOLS DEMO WITH CLARIFICATIONS")
    print("=" * 50)
    print("This demo will:")
    print("1. Try to read a config file (will show clarification if not found)")
    print("2. Configure narrator settings (will show clarification for invalid types)")
    print("3. Generate a summary")
    print()
    
    try:
        # Test the plan execution with Portia
        print("🚀 Executing plan...")
        result = portia.run(
            plan_definition=plan,
            inputs={
                "config_file": "nonexistent_config.json",  # This would trigger clarification
                "narrator_choice": "david"                 # Valid choice
            }
        )
        
        print("✅ Plan execution completed!")
        if result and hasattr(result, 'output'):
            print("\n📋 FINAL SUMMARY:")
            print("-" * 30)
            print(result.output)
        elif result:
            print(f"\n📋 RESULT: {result}")
        else:
            print("No output received")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n💡 NOTE: In a real scenario, clarifications would pause execution")
    print("and wait for user input to resolve the choices before continuing.")

if __name__ == "__main__":
    print("🛠️ PORTIA CUSTOM TOOLS WITH CLARIFICATIONS DEMO")
    print("📋 Showcasing MultipleChoiceClarification capabilities")
    print("=" * 60)
    demo_custom_tools()
