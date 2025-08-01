#!/usr/bin/env python3
"""
Send promotional SMS to DJ Martin
Back to School Braiding Special - $15 OFF
Target: DJ Martin (+12566946682)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from twilio.rest import Client
from config.settings import get_settings

def create_promo_message():
    """Create promotional SMS message for DJ Martin."""
    
    message = """🎒 Hey DJ! GetTwisted Hair Studios here with an exclusive Back to School special just for you!

✨ BACK TO SCHOOL BRAIDING SPECIAL ✨
💰 $15 OFF all braids & styling
⏰ This week only!

We know you love our braiding services and wanted to make sure you didn't miss this limited-time offer.

📅 Book now: Reply BOOK or call (610) 288-0343
ℹ️ More info: Reply INFO
🚫 Stop texts: Reply STOP

Ready to slay your back-to-school look? Let's get you scheduled! 💫

- Your friends at GetTwisted Hair Studios"""
    
    return message

def send_promotional_sms():
    """Send promotional SMS to DJ Martin."""
    
    print("📱 SENDING PROMOTIONAL SMS TO DJ MARTIN")
    print("=" * 60)
    
    # Load settings
    settings = get_settings()
    
    # DJ Martin's details
    target_phone = "+12566946682"
    customer_name = "DJ Martin"
    promotion = "Back to School Braiding Special"
    discount = "$15 OFF"
    
    print(f"🎯 Customer: {customer_name}")
    print(f"📱 Phone: {target_phone}")
    print(f"🎒 Promotion: {promotion}")
    print(f"💰 Discount: {discount}")
    print(f"📞 From: {settings.TWILIO_PHONE_NUMBER}")
    
    # Create promotional message
    message_body = create_promo_message()
    print(f"\n📝 Message created ({len(message_body)} characters)")
    print(f"📄 Preview:")
    print("-" * 40)
    print(message_body[:200] + "..." if len(message_body) > 200 else message_body)
    print("-" * 40)
    
    # Initialize Twilio client
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print(f"\n✅ Twilio client ready")
    except Exception as e:
        print(f"❌ Failed to initialize Twilio client: {e}")
        return False
    
    # Send the SMS
    try:
        print(f"\n🚀 SENDING PROMOTIONAL SMS...")
        print(f"   → Texting DJ Martin at {target_phone}")
        print(f"   → Delivering Back to School promotion")
        
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=target_phone
        )
        
        print(f"\n🎉 PROMOTIONAL SMS SENT SUCCESSFULLY!")
        print(f"   ✅ Message SID: {message.sid}")
        print(f"   ✅ Status: {message.status}")
        print(f"   ✅ Direction: {message.direction}")
        print(f"   ✅ Price: {message.price if message.price else 'TBD'}")
        
        # Log the promotional SMS
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📋 PROMOTIONAL SMS LOG:")
        print(f"   🕐 Timestamp: {timestamp}")
        print(f"   🆔 Message SID: {message.sid}")
        print(f"   👤 Customer: {customer_name}")
        print(f"   📱 Phone: {target_phone}")
        print(f"   🎒 Campaign: {promotion}")
        print(f"   💰 Offer: {discount}")
        print(f"   📞 From: GetTwisted Hair Studios ({settings.TWILIO_PHONE_NUMBER})")
        print(f"   📊 Characters: {len(message_body)}")
        
        return message.sid
        
    except Exception as e:
        print(f"❌ SMS FAILED: {e}")
        return False

def monitor_sms_results(message_sid):
    """Monitor the SMS and show expected results."""
    print(f"\n" + "=" * 60)
    print(f"📊 SMS MONITORING & EXPECTED RESULTS")
    print(f"=" * 60)
    
    print(f"📱 SMS Details:")
    print(f"   🆔 SID: {message_sid}")
    print(f"   🔗 Monitor: https://console.twilio.com/")
    
    print(f"\n🎯 Expected Customer Experience:")
    print(f"   1. 📱 DJ Martin receives text message")
    print(f"   2. 📖 Reads: 'Hey DJ! GetTwisted Hair Studios here...'")
    print(f"   3. 🎒 Sees: 'BACK TO SCHOOL BRAIDING SPECIAL - $15 OFF'")
    print(f"   4. ⌨️  Options: Reply BOOK, INFO, or STOP")
    print(f"   5. 📞 Can also call (610) 288-0343 directly")
    
    print(f"\n📈 Success Metrics:")
    print(f"   ✅ Message delivered (status: 'sent' → 'delivered')")
    print(f"   ✅ Customer opens message (read receipt)")
    print(f"   ✅ Customer engagement (reply or call)")
    print(f"   ✅ Potential booking conversion")
    
    print(f"\n🎯 Business Impact:")
    print(f"   💰 Revenue: Potential $15+ booking")
    print(f"   👤 Customer: Re-engagement with DJ Martin")
    print(f"   📈 Campaign: Back to School promotion launch")
    print(f"   🔄 Follow-up: Reply handling or phone call")

def show_campaign_summary():
    """Show campaign summary and next steps."""
    print(f"\n" + "=" * 60)
    print(f"🎒 BACK TO SCHOOL SMS CAMPAIGN - LAUNCH COMPLETE")
    print(f"=" * 60)
    
    print(f"✅ CAMPAIGN STATUS: ACTIVE")
    print(f"   🎯 Target Customer: DJ Martin")
    print(f"   📱 Contact Method: SMS text message via Twilio")
    print(f"   🎒 Promotion: Back to School Braiding Special")
    print(f"   💰 Discount: $15 OFF")
    print(f"   ⏰ Urgency: This week only")
    
    print(f"\n🚀 NEXT ACTIONS:")
    print(f"   1. 📊 Monitor message delivery in Twilio Console")
    print(f"   2. 📱 Handle customer replies (BOOK, INFO, STOP)")
    print(f"   3. 📞 Answer calls to (610) 288-0343")
    print(f"   4. 📅 Schedule appointment if customer replies BOOK")
    print(f"   5. 📈 Track campaign ROI and customer response")
    
    print(f"\n💡 SMS ADVANTAGES:")
    print(f"   ✅ No carrier blocking issues")
    print(f"   ✅ Higher open rates than voice calls")
    print(f"   ✅ Customer can respond at their convenience")
    print(f"   ✅ Clear call-to-action with reply options")
    print(f"   ✅ Cost-effective promotional channel")
    
    print(f"\n🔥 TwistyVoice AI Assistant: SMS CAMPAIGN LAUNCHED!")

if __name__ == "__main__":
    print("🔥 TwistyVoice - SMS PROMOTIONAL CAMPAIGN")
    print("🎒 Back to School Braiding Special")
    print("👤 Target: DJ Martin")
    print("💰 Offer: $15 OFF back-to-school braids")
    print("📱 Method: SMS Text Message")
    print()
    
    # Final confirmation
    confirm = input("📱 CONFIRMATION: Send promotional SMS to DJ Martin? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Promotional SMS cancelled")
        sys.exit(0)
    
    print("\n📱 LAUNCHING SMS CAMPAIGN...")
    
    message_sid = send_promotional_sms()
    
    if message_sid:
        monitor_sms_results(message_sid)
        show_campaign_summary()
        
        print(f"\n🎉 PROMOTIONAL SMS TO DJ MARTIN SENT!")
        print(f"📱 DJ Martin will receive the Back to School promotion text NOW!")
        
    else:
        print(f"\n❌ SMS campaign failed. Check errors above.")
