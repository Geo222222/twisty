#!/usr/bin/env python3
"""
Test promotional call using a verified number.
This will call YOUR verified number to test the TwistyVoice system.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from twilio.rest import Client
from config.settings import get_settings

def create_test_twiml():
    """Create TwiML for testing the promotional system."""
    
    twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="en-US">
        Hello! This is a test call from TwistyVoice promotional system.
        You are hearing this because the system is working correctly.
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        This would normally be DJ Martin receiving a Back to School braiding special offer.
        The promotion would offer 15 dollars off all back-to-school braids.
    </Say>
    <Pause length="1"/>
    <Gather action="https://handler.twilio.com/twiml/EH123" method="POST" numDigits="1" timeout="10">
        <Say voice="alice" language="en-US">
            To test the booking system, press 1.
            For more information, press 2.
            This is just a test of the TwistyVoice promotional calling system.
        </Say>
    </Gather>
    <Say voice="alice" language="en-US">
        Test complete. The TwistyVoice promotional system is working correctly.
        Thank you for testing!
    </Say>
    <Hangup/>
</Response>'''
    
    return twiml

def get_verified_numbers():
    """Get list of verified numbers from Twilio."""
    settings = get_settings()
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        outgoing_caller_ids = client.outgoing_caller_ids.list()
        verified_numbers = [caller_id.phone_number for caller_id in outgoing_caller_ids]
        return verified_numbers
    except Exception as e:
        print(f"❌ Error getting verified numbers: {e}")
        return []

def make_test_call(target_phone):
    """Make a test promotional call."""
    
    print("📞 MAKING TEST PROMOTIONAL CALL")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    
    print(f"🔧 Twilio Configuration:")
    print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"   From Number: {settings.TWILIO_PHONE_NUMBER}")
    
    print(f"\n🎯 Test Call Details:")
    print(f"   To: {target_phone}")
    print(f"   From: {settings.TWILIO_PHONE_NUMBER}")
    print(f"   Purpose: Test TwistyVoice promotional system")
    
    # Create TwiML
    twiml = create_test_twiml()
    print(f"\n📝 TwiML Created ({len(twiml)} characters)")
    
    # Initialize Twilio client
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print(f"\n✅ Twilio client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Twilio client: {e}")
        return False
    
    # Make the call
    try:
        print(f"\n🚀 INITIATING TEST CALL...")
        print(f"   Calling {target_phone}...")
        
        call = client.calls.create(
            twiml=twiml,
            to=target_phone,
            from_=settings.TWILIO_PHONE_NUMBER
        )
        
        print(f"✅ TEST CALL INITIATED SUCCESSFULLY!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   Direction: {call.direction}")
        
        # Log the call
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📋 Call Log:")
        print(f"   Timestamp: {timestamp}")
        print(f"   Call SID: {call.sid}")
        print(f"   To: {target_phone}")
        print(f"   From: {settings.TWILIO_PHONE_NUMBER}")
        print(f"   Type: TwistyVoice System Test")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ Failed to make call: {e}")
        return False

def show_next_steps():
    """Show next steps for production use."""
    print(f"\n" + "=" * 50)
    print(f"🚀 NEXT STEPS FOR PRODUCTION")
    print(f"=" * 50)
    print(f"📋 To call real customers:")
    print(f"   1. Verify customer phone numbers in Twilio Console")
    print(f"   2. OR upgrade to paid Twilio account (removes verification requirement)")
    print(f"   3. Set up ngrok for webhook responses")
    print(f"")
    print(f"🔗 Twilio Console: https://console.twilio.com/")
    print(f"   → Phone Numbers → Manage → Verified Caller IDs")
    print(f"   → Add +2566946682 (DJ Martin's number)")
    print(f"")
    print(f"💳 Upgrade Account:")
    print(f"   → Account → Billing → Add payment method")
    print(f"   → Removes trial restrictions")
    print(f"   → Enables calls to any number")

if __name__ == "__main__":
    print("🔥 TwistyVoice - SYSTEM TEST CALL")
    print("🧪 Testing promotional calling system")
    print()
    
    # Get verified numbers
    print("🔍 Checking verified numbers...")
    verified_numbers = get_verified_numbers()
    
    if verified_numbers:
        print(f"✅ Found {len(verified_numbers)} verified number(s):")
        for i, number in enumerate(verified_numbers, 1):
            print(f"   {i}. {number}")
        
        # Use first verified number for test
        target_phone = verified_numbers[0]
        print(f"\n🎯 Will call: {target_phone}")
        
        # Confirm before making test call
        confirm = input(f"\n⚠️  This will make a TEST call to {target_phone}. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Test call cancelled by user")
            sys.exit(0)
        
        call_sid = make_test_call(target_phone)
        
        if call_sid:
            print(f"\n🎉 TEST CALL INITIATED!")
            print(f"📞 Your phone should be ringing now!")
            print(f"🆔 Call SID: {call_sid}")
            show_next_steps()
        else:
            print(f"\n❌ Test call failed. Check the errors above.")
    
    else:
        print("❌ No verified numbers found!")
        print("📋 You need to verify at least one phone number in Twilio Console")
        print("🔗 Go to: https://console.twilio.com/")
        print("   → Phone Numbers → Manage → Verified Caller IDs")
        show_next_steps()
