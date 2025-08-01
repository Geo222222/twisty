#!/usr/bin/env python3
"""
REAL PROMOTIONAL CALL TO DJ MARTIN
Back to School Braiding Special - $15 OFF
Target: DJ Martin (+2566946682)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from twilio.rest import Client
from config.settings import get_settings

def create_dj_martin_twiml():
    """Create personalized TwiML for DJ Martin's Back to School promotion."""
    
    twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="en-US">
        Hi DJ! This is TwistyVoice calling from GetTwisted Hair Studios. 
        We hope you're doing well!
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        We're excited to let you know about our Back to School Braiding Special, 
        just for valued clients like you. We're offering 15 dollars off all 
        back-to-school braids and styling services.
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        This special offer is valid through this week only, and we have 
        appointments available with our top stylists who specialize in braids.
    </Say>
    <Pause length="1"/>
    <Gather action="https://handler.twilio.com/twiml/EH123" method="POST" numDigits="1" timeout="15">
        <Say voice="alice" language="en-US">
            If you'd like to book your back-to-school style appointment now, press 1.
            For more information about our services or to request a callback, press 2.
            We can't wait to help you look amazing for the new school year!
            Press 1 now to secure your appointment with the 15 dollar discount.
        </Say>
    </Gather>
    <Say voice="alice" language="en-US">
        No worries if you missed that! We'll send you a text message with all the details 
        about our Back to School special. You can also call us directly at GetTwisted Hair Studios.
        Have a wonderful day, DJ!
    </Say>
    <Hangup/>
</Response>'''
    
    return twiml

def make_dj_martin_call():
    """Make the real promotional call to DJ Martin."""
    
    print("📞 CALLING DJ MARTIN - BACK TO SCHOOL SPECIAL")
    print("=" * 60)
    
    # Load settings
    settings = get_settings()
    
    # DJ Martin's details (using verified number format)
    target_phone = "+12566946682"
    customer_name = "DJ Martin"
    promotion = "Back to School Braiding Special"
    discount = "$15 OFF"
    
    print(f"🎯 Customer: {customer_name}")
    print(f"📱 Phone: {target_phone}")
    print(f"🎒 Promotion: {promotion}")
    print(f"💰 Discount: {discount}")
    print(f"📞 From: {settings.TWILIO_PHONE_NUMBER}")
    
    # Create personalized TwiML
    twiml = create_dj_martin_twiml()
    print(f"\n📝 Personalized TwiML created ({len(twiml)} characters)")
    
    # Initialize Twilio client
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print(f"✅ Twilio client ready")
    except Exception as e:
        print(f"❌ Failed to initialize Twilio client: {e}")
        return False
    
    # Make the promotional call
    try:
        print(f"\n🚀 INITIATING PROMOTIONAL CALL...")
        print(f"   → Calling DJ Martin at {target_phone}")
        print(f"   → Delivering Back to School promotion")
        
        call = client.calls.create(
            twiml=twiml,
            to=target_phone,
            from_=settings.TWILIO_PHONE_NUMBER
        )
        
        print(f"\n🎉 PROMOTIONAL CALL SUCCESSFUL!")
        print(f"   ✅ Call SID: {call.sid}")
        print(f"   ✅ Status: {call.status}")
        print(f"   ✅ Direction: {call.direction}")
        
        # Log the promotional call
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📋 PROMOTIONAL CALL LOG:")
        print(f"   🕐 Timestamp: {timestamp}")
        print(f"   🆔 Call SID: {call.sid}")
        print(f"   👤 Customer: {customer_name}")
        print(f"   📱 Phone: {target_phone}")
        print(f"   🎒 Campaign: {promotion}")
        print(f"   💰 Offer: {discount}")
        print(f"   📞 From: GetTwisted Hair Studios ({settings.TWILIO_PHONE_NUMBER})")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ CALL FAILED: {e}")
        return False

def monitor_call_results(call_sid):
    """Monitor the call and show expected results."""
    print(f"\n" + "=" * 60)
    print(f"📊 CALL MONITORING & EXPECTED RESULTS")
    print(f"=" * 60)
    
    print(f"📞 Call Details:")
    print(f"   🆔 SID: {call_sid}")
    print(f"   🔗 Monitor: https://console.twilio.com/")
    
    print(f"\n🎯 Expected Customer Experience:")
    print(f"   1. 📱 DJ Martin's phone rings")
    print(f"   2. 🎤 Hears: 'Hi DJ! This is TwistyVoice from GetTwisted...'")
    print(f"   3. 🎒 Promotion: 'Back to School Braiding Special - $15 OFF'")
    print(f"   4. ⌨️  Options: Press 1 to book, Press 2 for info")
    print(f"   5. 📝 If no response: Text message follow-up mentioned")
    
    print(f"\n📈 Success Metrics:")
    print(f"   ✅ Call connects (status: 'in-progress' → 'completed')")
    print(f"   ✅ Duration: 45+ seconds (full message)")
    print(f"   ✅ Customer engagement (button press)")
    print(f"   ✅ Potential booking conversion")
    
    print(f"\n🎯 Business Impact:")
    print(f"   💰 Revenue: Potential $15+ booking")
    print(f"   👤 Customer: Re-engagement with DJ Martin")
    print(f"   📈 Campaign: Back to School promotion launch")
    print(f"   🔄 Follow-up: Text message or callback opportunity")

def show_campaign_summary():
    """Show campaign summary and next steps."""
    print(f"\n" + "=" * 60)
    print(f"🎒 BACK TO SCHOOL CAMPAIGN - LAUNCH COMPLETE")
    print(f"=" * 60)
    
    print(f"✅ CAMPAIGN STATUS: ACTIVE")
    print(f"   🎯 Target Customer: DJ Martin")
    print(f"   📱 Contact Method: Voice call via Twilio")
    print(f"   🎒 Promotion: Back to School Braiding Special")
    print(f"   💰 Discount: $15 OFF")
    print(f"   ⏰ Urgency: This week only")
    
    print(f"\n🚀 NEXT ACTIONS:")
    print(f"   1. 📊 Monitor call completion in Twilio Console")
    print(f"   2. 📱 Follow up with text message if needed")
    print(f"   3. 📞 Handle any callback requests")
    print(f"   4. 📅 Schedule appointment if customer presses 1")
    print(f"   5. 📈 Track campaign ROI and customer response")
    
    print(f"\n🔥 TwistyVoice AI Assistant: MISSION ACCOMPLISHED!")

if __name__ == "__main__":
    print("🔥 TwistyVoice - REAL PROMOTIONAL CAMPAIGN")
    print("🎒 Back to School Braiding Special")
    print("👤 Target: DJ Martin")
    print("💰 Offer: $15 OFF back-to-school braids")
    print()
    
    # Final confirmation
    confirm = input("🚨 FINAL CONFIRMATION: Make REAL promotional call to DJ Martin? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Promotional call cancelled")
        sys.exit(0)
    
    print("\n🎬 LAUNCHING PROMOTIONAL CAMPAIGN...")
    
    call_sid = make_dj_martin_call()
    
    if call_sid:
        monitor_call_results(call_sid)
        show_campaign_summary()
        
        print(f"\n🎉 PROMOTIONAL CALL TO DJ MARTIN COMPLETED!")
        print(f"📞 DJ Martin is receiving the Back to School promotion NOW!")
        
    else:
        print(f"\n❌ Promotional campaign failed. Check errors above.")
