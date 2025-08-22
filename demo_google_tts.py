#!/usr/bin/env python3
"""
Demo script for Celebrity Companion AI with Google TTS
=====================================================

This script demonstrates the basic functionality without requiring
full Google Cloud setup. It will show text responses and indicate
when TTS would be available.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_setup():
    """Check if the required setup is complete"""
    print("🔍 Checking setup requirements...")
    
    # Check Google API key
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        print("✅ GOOGLE_API_KEY found")
    else:
        print("❌ GOOGLE_API_KEY not found - add to .env file")
        print("   Get it from: https://aistudio.google.com/")
    
    # Check Google Cloud credentials
    google_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if google_creds:
        if os.path.exists(google_creds):
            print("✅ GOOGLE_APPLICATION_CREDENTIALS found and file exists")
        else:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS file not found")
    else:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set - TTS will be text-only")
        print("   Set up Google Cloud TTS for voice output")
    
    # Check if required packages are installed
    try:
        import google.generativeai
        print("✅ Google Generative AI package available")
    except ImportError:
        print("❌ Google Generative AI package not available")
        print("   Run: pip install google-generativeai")
    
    try:
        from google.cloud import texttospeech
        print("✅ Google Cloud TTS package available")
    except ImportError:
        print("❌ Google Cloud TTS package not available")
        print("   Run: pip install google-cloud-texttospeech")
    
    print()

def show_usage():
    """Show how to use the system"""
    print("📖 Usage Instructions:")
    print("=" * 50)
    
    print("\n1. Set up environment variables in .env file:")
    print("   GOOGLE_API_KEY=your_gemini_api_key_here")
    print("   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json")
    
    print("\n2. Run the main script:")
    print("   python3 celebrity_companion_ai_clean.py")
    
    print("\n3. Available commands:")
    print("   - Type normally to chat with celebrities")
    print("   - 'switch to [celebrity]' to change voices")
    print("   - 'quit' to exit")
    
    print("\n4. Available celebrities:")
    print("   - scarlett (Scarlett Johansson)")
    print("   - morgan (Morgan Freeman)")
    print("   - david (David Attenborough)")
    print("   - peter (Peter Griffin)")
    
    print("\n5. Voice switching examples:")
    print("   'switch to morgan'")
    print("   'change to david'")
    print("   'talk to scarlett'")
    
    print()

def show_setup_steps():
    """Show detailed setup steps"""
    print("🔧 Detailed Setup Steps:")
    print("=" * 50)
    
    print("\n1. Get Google Gemini API Key:")
    print("   - Go to https://aistudio.google.com/")
    print("   - Click 'Get API key'")
    print("   - Create new API key")
    print("   - Copy to .env file")
    
    print("\n2. Set up Google Cloud TTS:")
    print("   - Go to https://console.cloud.google.com/")
    print("   - Create new project or select existing")
    print("   - Enable Cloud Text-to-Speech API")
    print("   - Create service account with 'Cloud Text-to-Speech User' role")
    print("   - Download JSON key file")
    print("   - Set path in .env file")
    
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n4. Test the system:")
    print("   python3 celebrity_companion_ai_clean.py")
    
    print()

def main():
    """Main demo function"""
    print("🎭🔊 Celebrity Companion AI - Google TTS Demo")
    print("=" * 60)
    
    check_setup()
    show_usage()
    show_setup_steps()
    
    print("💡 For full setup guide, see: GOOGLE_TTS_SETUP.md")
    print("🎯 Ready to run: python3 celebrity_companion_ai_clean.py")

if __name__ == "__main__":
    main()
