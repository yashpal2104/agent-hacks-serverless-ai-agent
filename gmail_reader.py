#!/usr/bin/env python3
"""
📧 Gmail Reader Wrapper - Streamlit Compatibility Layer
======================================================
Provides GmailReader class that wraps the enhanced task-based celebrity Gmail reader
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Import the enhanced functions from the better implementation
try:
    from task_based_celebrity_gmail import (
        AdvancedCelebrityVoice, 
        setup_content_generator, 
        generate_celebrity_script
    )
    ENHANCED_GMAIL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced Gmail reader not available: {e}")
    ENHANCED_GMAIL_AVAILABLE = False

# Import Portia components
try:
    from portia import (
        ActionClarification,
        InputClarification,
        MultipleChoiceClarification,
        PlanRunState,
        Portia,
        PortiaToolRegistry,
        default_config,
    )
    PORTIA_AVAILABLE = True
except ImportError:
    PORTIA_AVAILABLE = False

load_dotenv()

class GmailReader:
    """
    Streamlit-compatible Gmail Reader that wraps the enhanced task-based implementation
    """
    
    def __init__(self):
        self.authenticated = False
        self.portia = None
        
        # Initialize enhanced voice engine if available
        if ENHANCED_GMAIL_AVAILABLE:
            self.voice_engine = AdvancedCelebrityVoice()
            self.content_model = setup_content_generator()
        else:
            self.voice_engine = None
            self.content_model = None
    
    def authenticate_with_portia(self):
        """Authenticate with Portia for Gmail access"""
        if not PORTIA_AVAILABLE:
            print("❌ Portia not available for Gmail authentication")
            return False
        
        try:
            print("🔧 Setting up Portia with Gmail tools...")
            config = default_config()
            
            # Configure working Claude model
            working_model = "anthropic/claude-3-5-haiku-20241022"
            config.models.default_model = working_model
            config.models.planning_model = working_model
            config.models.execution_model = working_model
            config.models.introspection_model = working_model
            
            self.portia = Portia(tools=PortiaToolRegistry(config), config=config)
            self.authenticated = True
            print("✅ Portia configured with Gmail tools")
            return True
            
        except Exception as e:
            print(f"⚠️ Portia setup failed: {e}")
            return False
    
    def get_emails_with_portia(self, sender_email=None, max_results=10):
        """Get emails using Portia Gmail tools"""
        if not self.authenticated:
            if not self.authenticate_with_portia():
                return []
        
        try:
            # Create Gmail reading task (using the enhanced approach)
            if sender_email and sender_email.strip():
                task = f"Search Gmail for emails from {sender_email.strip()} and provide a detailed summary of each email. Read each email in order and provide the content clearly."
            else:
                task = f"Get the most recent {max_results} emails from Gmail and provide a detailed summary including sender, subject, date, and key content from each email."
            
            print(f"📧 Executing enhanced Gmail task...")
            plan_run = self.portia.run(task)
            
            # Handle clarifications (enhanced from task-based approach)
            clarification_count = 0
            while plan_run.state == PlanRunState.NEED_CLARIFICATION and clarification_count < 5:
                clarification_count += 1
                print(f"\n🔐 Gmail authentication required (Step {clarification_count})...")
                
                for clarification in plan_run.get_outstanding_clarifications():
                    if isinstance(clarification, ActionClarification):
                        print(f"{clarification.user_guidance}")
                        print(f"🔗 Authentication URL: {clarification.action_url}")
                        input("Complete authentication in browser, then press Enter to continue...")
                        
                    elif isinstance(clarification, InputClarification):
                        user_input = input(f"{clarification.prompt}: ")
                        clarification.respond(user_input)
                        
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
                                clarification.respond(clarification.options[0])
                        except ValueError:
                            clarification.respond(clarification.options[0])
                
                plan_run = self.portia.resume(plan_run)
            
            print(f"📊 Task status: {plan_run.state}")
            
            # Extract Gmail content (enhanced method)
            gmail_content = ""
            if hasattr(plan_run, 'result') and plan_run.result:
                gmail_content = str(plan_run.result)
            elif hasattr(plan_run, 'outputs') and plan_run.outputs:
                gmail_content = str(plan_run.outputs)
            
            # Fallback extraction
            if not gmail_content:
                plan_data = str(plan_run)
                if any(keyword in plan_data.lower() for keyword in ['email', 'gmail', 'devops', 'job', 'subject']):
                    gmail_content = plan_data
            
            if gmail_content and len(gmail_content.strip()) > 50:
                print("✅ Gmail content retrieved via enhanced Portia integration!")
                return self._parse_portia_emails(gmail_content)
                
            print("📭 No emails retrieved")
            return []
            
        except Exception as e:
            print(f"❌ Enhanced Portia Gmail error: {e}")
            return []
    
    def _parse_portia_emails(self, gmail_content):
        """Parse email content from Portia response"""
        # Create email structure from Portia content
        emails = [{
            'id': 'portia-email-enhanced',
            'subject': 'Gmail Summary via Enhanced Portia',
            'sender': 'Gmail via Task-Based Portia',
            'formatted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'body': gmail_content,
            'labels': ['INBOX'],
            'snippet': gmail_content[:200] + "..." if len(gmail_content) > 200 else gmail_content
        }]
        return emails
    
    def summarize_emails_with_celebrity(self, emails, celebrity_name="David Attenborough"):
        """Generate celebrity-narrated email summaries using enhanced script generation"""
        if not emails:
            return "No recent emails to summarize!"
        
        if not ENHANCED_GMAIL_AVAILABLE or not self.content_model:
            # Fallback to simple summary
            return f"{celebrity_name} would love to tell you about your emails, but the enhanced voice system isn't available right now."
        
        # Use the enhanced script generation from task_based_celebrity_gmail.py
        gmail_content = ""
        for email in emails:
            gmail_content += f"Email: {email.get('subject', 'No Subject')}\n"
            gmail_content += f"From: {email.get('sender', 'Unknown')}\n"
            gmail_content += f"Content: {email.get('body', email.get('snippet', ''))}\n\n"
        
        try:
            # Generate enhanced celebrity script with voice descriptions
            script = generate_celebrity_script(
                self.content_model, 
                celebrity_name, 
                gmail_content, 
                self.voice_engine
            )
            return script
            
        except Exception as e:
            print(f"⚠️ Enhanced email analysis failed: {e}")
            return f"I'm afraid {celebrity_name} is having some technical difficulties with the enhanced voice system right now."
    
    def speak_email_summary(self, summary, celebrity_name, speed=1.0, pitch=0.0):
        """Speak email summary with enhanced natural celebrity voice"""
        if ENHANCED_GMAIL_AVAILABLE and self.voice_engine:
            try:
                self.voice_engine.speak_as_celebrity(summary, celebrity_name)
                return True
            except Exception as e:
                print(f"❌ Enhanced voice playback error: {e}")
                return False
        else:
            print(f"🗣️ {celebrity_name} says (text-only - enhanced voices unavailable):")
            print("─" * 40)
            print(summary)
            print("─" * 40)
            return False
    
    def stop_narration(self):
        """Stop current narration"""
        if ENHANCED_GMAIL_AVAILABLE and self.voice_engine:
            try:
                self.voice_engine.stop_speaking()
                print("⏹️ Enhanced voice narration stopped")
            except:
                pass
        else:
            print("⚠️ No enhanced voice system to stop")

# For backwards compatibility and direct usage
def main():
    """Test the enhanced Gmail reader functionality"""
    print("📧 Enhanced Celebrity Gmail Email Reader (Streamlit Compatible)")
    print("=" * 60)
    
    gmail = GmailReader()
    
    if not gmail.authenticate_with_portia():
        print("❌ Gmail authentication failed.")
        return
    
    print("\n📬 Testing enhanced Gmail functionality...")
    emails = gmail.get_emails_with_portia(max_results=5)
    
    if emails:
        print(f"✅ Found {len(emails)} emails")
        
        # Test celebrity summary
        celebrity = "David Attenborough"
        print(f"\n🎭 Testing {celebrity}'s enhanced email analysis...")
        
        summary = gmail.summarize_emails_with_celebrity(emails, celebrity)
        print(f"📝 Enhanced Summary:\n{summary}")
        
        # Test voice (if available)
        if ENHANCED_GMAIL_AVAILABLE:
            test_voice = input(f"\nTest {celebrity}'s enhanced natural voice? (y/n): ").lower().startswith('y')
            if test_voice:
                print("🔊 Playing enhanced natural voice...")
                gmail.speak_email_summary(summary, celebrity)
    else:
        print("📪 No emails retrieved")

if __name__ == "__main__":
    main()
