#!/usr/bin/env python3
"""
Make a real promotional call using Twilio integration.
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

def make_promotional_call():
    """Make a real promotional call to DJ Martin."""
    
    print("📞 MAKING REAL PROMOTIONAL CALL")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    
    print(f"🔧 Twilio Configuration:")
    print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"   From Number: {settings.TWILIO_PHONE_NUMBER}")
    print(f"   Webhook URL: {settings.TWILIO_WEBHOOK_URL}")
    
    # Target customer (DJ Martin)
    target_phone = "+2566946682"  # DJ Martin's number from CSV
    customer_id = 1
    promotion_id = 3  # Back to School Braiding Special
    
    print(f"\n🎯 Call Details:")
    print(f"   To: {target_phone}")
    print(f"   From: {settings.TWILIO_PHONE_NUMBER}")
    print(f"   Customer ID: {customer_id}")
    print(f"   Promotion ID: {promotion_id}")
    
    # Create TwiML URL for this specific call
    twiml_url = f"{settings.TWILIO_WEBHOOK_URL}/api/v1/twiml/promotional_call?customer_id={customer_id}&promotion_id={promotion_id}"
    print(f"   TwiML URL: {twiml_url}")
    
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
            url=twiml_url,
            to=target_phone,
            from_=settings.TWILIO_PHONE_NUMBER,
            method='GET'
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
        print(f"   TwiML URL: {twiml_url}")
        print(f"   Promotion: Back to School Braiding Special")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to make call: {e}")
        return False

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
    print(f"📱 Customer Response Tracking:")
    print(f"   - If customer presses 1: Booking webhook will be called")
    print(f"   - If customer presses 2: Info request logged")
    print(f"   - If customer presses 9: Opt-out processed")
    print(f"")
    print(f"🔗 Webhook Endpoints:")
    print(f"   - Response Handler: POST /api/v1/webhooks/gather_response")
    print(f"   - Call Status: POST /api/v1/webhooks/call_status")
    print(f"")
    print(f"📊 Check Results:")
    print(f"   - GET /api/v1/admin/customers/1/conversations")
    print(f"   - GET /api/v1/admin/bookings")

if __name__ == "__main__":
    print("🔥 TwistyVoice - REAL CALL EXECUTION")
    print("🎒 Back to School Braiding Special")
    print("📞 Target: DJ Martin (+2566946682)")
    print()
    
    # Confirm before making real call
    confirm = input("⚠️  This will make a REAL phone call. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Call cancelled by user")
        sys.exit(0)
    
    success = make_promotional_call()
    
    if success:
        show_monitoring_info()
        print(f"\n🎉 REAL PROMOTIONAL CALL INITIATED!")
        print(f"📞 DJ Martin should be receiving the call now!")
    else:
        print(f"\n❌ Call failed. Check the errors above.")
