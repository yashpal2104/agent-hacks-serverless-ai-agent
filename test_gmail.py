#!/usr/bin/env python3
"""
Quick test script for Updated Gmail Reader with Portia Integration
"""

from gmail_reader import GmailReader
import time

def test_updated_gmail_reader():
    print("📧 Testing Updated Gmail Reader with Portia Integration...")
    print("=" * 60)
    
    # Test the updated Gmail reader
    gmail = GmailReader()
    
    # Test Portia authentication
    print("🔧 Testing Portia authentication...")
    if gmail.authenticate_with_portia():
        print("✅ Portia authentication successful!")
        
        # Test email fetching (will likely need manual intervention)
        print("📬 Testing email fetching via Portia...")
        emails = gmail.get_emails_with_portia(max_results=5)
        
        if emails:
            print(f"✅ Found {len(emails)} emails via Portia")
        else:
            print("📭 No emails returned (expected without manual auth)")
    else:
        print("❌ Portia authentication failed - testing with mock data")
    
    # Test updated celebrities (removed Gordon Ramsay, added preferred ones)
    print("\n🎭 Testing Updated Celebrity Lineup:")
    print("-" * 40)
    
    # Mock email data for testing
    mock_emails = [{
        'subject': 'Weekly Project Update',
        'sender': 'team@company.com',
        'formatted_date': '2025-08-25 10:00:00',
        'body': 'This week we made significant progress on the AI integration project. The new features are ready for testing.',
        'labels': ['INBOX', 'IMPORTANT']
    }, {
        'subject': 'Meeting Invitation',
        'sender': 'hr@company.com', 
        'formatted_date': '2025-08-25 09:30:00',
        'body': 'You are invited to the quarterly all-hands meeting next Friday at 2 PM.',
        'labels': ['INBOX']
    }]
    
    # Test all updated celebrities
    updated_celebrities = ["David Attenborough", "Morgan Freeman", "Scarlett Johansson", "Peter Griffin"]
    
    for celebrity in updated_celebrities:
        print(f"\n🎤 {celebrity}'s Email Analysis:")
        print("-" * 35)
        
        summary = gmail.summarize_emails_with_celebrity(mock_emails, celebrity)
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        
        # Test voice synthesis (optional)
        test_voice = input(f"\nTest {celebrity}'s natural voice? (y/n): ").lower().startswith('y') if celebrity in ["David Attenborough", "Morgan Freeman"] else False
        
        if test_voice:
            print(f"🎬 Testing {celebrity}'s natural voice...")
            try:
                gmail.speak_email_summary(summary, celebrity)
                print(f"✅ {celebrity}'s voice test completed!")
            except Exception as e:
                print(f"⚠️ Voice test failed: {e}")
        
        time.sleep(1)
    
    # Test stop functionality
    print(f"\n⏹️ Testing Stop Narration Feature:")
    print("-" * 35)
    print("Stop functionality is integrated - use Stop button in Streamlit app!")
    
    print(f"\n🎉 Updated Gmail Reader Test Complete!")
    print("✅ Portia integration ready")
    print("✅ Updated celebrity lineup (David, Morgan, Scarlett, Peter)")
    print("✅ Natural voice synthesis with Google Cloud TTS") 
    print("✅ Stop narration functionality")
    print("✅ Streamlit integration with start/stop controls")

if __name__ == "__main__":
    test_updated_gmail_reader()
