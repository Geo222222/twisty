#!/usr/bin/env python3
"""
Make a real promotional call using direct TwiML (no webhook required).
This will actually call DJ Martin's phone with the Back to School promotion.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from twilio.rest import Client
from config.settings import get_settings

def create_back_to_school_twiml():
    """Create TwiML for the Back to School promotion."""
    
    twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="en-US">
        Hi DJ, this is TwistyVoice calling from GetTwisted Hair Studios! 
        We're celebrating Back to School with a braiding special just for you.
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        We're offering 15 dollars off all back-to-school braids, 
        valid this week only with select stylists.
    </Say>
    <Pause length="1"/>
    <Gather action="https://handler.twilio.com/twiml/EH123" method="POST" numDigits="1" timeout="10">
        <Say voice="alice" language="en-US">
            If you'd like to book your style now, press 1.
            Need more info or a callback? Press 2.
            We can't wait to help you slay your back-to-school look!
            Press 1 now to book your appointment.
        </Say>
    </Gather>
    <Say voice="alice" language="en-US">
        I didn't receive a response. We'll send you a text message with the details. 
        Have a wonderful day!
    </Say>
    <Hangup/>
</Response>'''
    
    return twiml

def make_promotional_call():
    """Make a real promotional call to DJ Martin."""
    
    print("📞 MAKING REAL PROMOTIONAL CALL")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    
    print(f"🔧 Twilio Configuration:")
    print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"   From Number: {settings.TWILIO_PHONE_NUMBER}")
    
    # Target customer (DJ Martin)
    target_phone = "+2566946682"  # DJ Martin's number from CSV
    
    print(f"\n🎯 Call Details:")
    print(f"   To: {target_phone}")
    print(f"   From: {settings.TWILIO_PHONE_NUMBER}")
    print(f"   Promotion: Back to School Braiding Special")
    print(f"   Discount: $15 OFF")
    
    # Create TwiML
    twiml = create_back_to_school_twiml()
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
        print(f"\n🚀 INITIATING CALL...")
        print(f"   Calling {target_phone}...")
        
        call = client.calls.create(
            twiml=twiml,
            to=target_phone,
            from_=settings.TWILIO_PHONE_NUMBER
        )
        
        print(f"✅ CALL INITIATED SUCCESSFULLY!")
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
        print(f"   Promotion: Back to School Braiding Special")
        print(f"   Message: $15 OFF back-to-school braids")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ Failed to make call: {e}")
        return False

def check_call_status(call_sid):
    """Check the status of the call."""
    settings = get_settings()
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        call = client.calls(call_sid).fetch()
        print(f"\n📊 Call Status Update:")
        print(f"   SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   Duration: {call.duration} seconds" if call.duration else "   Duration: In progress")
        print(f"   Price: {call.price}" if call.price else "   Price: TBD")
        return call.status
    except Exception as e:
        print(f"❌ Error checking call status: {e}")
        return None

def show_monitoring_info():
    """Show how to monitor the call."""
    print(f"\n" + "=" * 50)
    print(f"📊 CALL MONITORING")
    print(f"=" * 50)
    print(f"🔍 Check Call Status:")
    print(f"   - Twilio Console: https://console.twilio.com/")
    print(f"   - Look for calls from +18882322251")
    print(f"   - Monitor call duration and status")
    print(f"")
    print(f"📱 Expected Customer Experience:")
    print(f"   1. Phone rings on +2566946682")
    print(f"   2. DJ Martin hears: 'Hi DJ, this is TwistyVoice...'")
    print(f"   3. Promotion message: '$15 OFF back-to-school braids'")
    print(f"   4. Options: Press 1 to book, Press 2 for info")
    print(f"   5. If no response: Goodbye message")
    print(f"")
    print(f"🎯 Success Indicators:")
    print(f"   - Call status: 'completed'")
    print(f"   - Duration: 30+ seconds (full message played)")
    print(f"   - Customer response logged (if they press buttons)")

if __name__ == "__main__":
    print("🔥 TwistyVoice - REAL CALL EXECUTION")
    print("🎒 Back to School Braiding Special")
    print("📞 Target: DJ Martin (+2566946682)")
    print("💰 Offer: $15 OFF back-to-school braids")
    print()
    
    # Confirm before making real call
    confirm = input("⚠️  This will make a REAL phone call to DJ Martin. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Call cancelled by user")
        sys.exit(0)
    
    call_sid = make_promotional_call()
    
    if call_sid:
        show_monitoring_info()
        print(f"\n🎉 REAL PROMOTIONAL CALL INITIATED!")
        print(f"📞 DJ Martin should be receiving the call now!")
        print(f"🆔 Call SID: {call_sid}")
        
        # Wait a moment then check status
        print(f"\n⏳ Checking call status in 5 seconds...")
        import time
        time.sleep(5)
        check_call_status(call_sid)
        
    else:
        print(f"\n❌ Call failed. Check the errors above.")
