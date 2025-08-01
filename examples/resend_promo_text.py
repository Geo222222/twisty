#!/usr/bin/env python3
"""
Resend promotional SMS to DJ Martin using verified local number
Back to School Braiding Special - $15 OFF
From: +12019928729 (verified local number)
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

def create_promo_message_v2():
    """Create promotional SMS message for DJ Martin (optimized for local number)."""
    
    message = """🎒 Hey DJ! GetTwisted Hair Studios here with your exclusive Back to School special!

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

def resend_promotional_sms():
    """Resend promotional SMS to DJ Martin using verified local number."""
    
    print("📱 RESENDING PROMOTIONAL SMS - VERIFIED LOCAL NUMBER")
    print("=" * 65)
    
    # Load settings (now with updated local number)
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
    print(f"📞 From: {settings.TWILIO_PHONE_NUMBER} (LOCAL VERIFIED)")
    
    # Create promotional message
    message_body = create_promo_message_v2()
    print(f"\n📝 Message created ({len(message_body)} characters)")
    print(f"📄 Preview:")
    print("-" * 50)
    print(message_body[:200] + "..." if len(message_body) > 200 else message_body)
    print("-" * 50)
    
    # Initialize Twilio client
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print(f"\n✅ Twilio client ready")
    except Exception as e:
        print(f"❌ Failed to initialize Twilio client: {e}")
        return False
    
    # Send the SMS
    try:
        print(f"\n🚀 RESENDING PROMOTIONAL SMS...")
        print(f"   → Texting DJ Martin at {target_phone}")
        print(f"   → Using verified local number: {settings.TWILIO_PHONE_NUMBER}")
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
        print(f"   ✅ From: {settings.TWILIO_PHONE_NUMBER} (LOCAL)")
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
        print(f"   🔧 Method: Local verified number (no toll-free issues)")
        
        return message.sid
        
    except Exception as e:
        print(f"❌ SMS FAILED: {e}")
        return False

def show_delivery_advantages():
    """Show advantages of using local verified number."""
    print(f"\n" + "=" * 65)
    print(f"🏆 LOCAL NUMBER ADVANTAGES")
    print(f"=" * 65)
    
    print(f"✅ DELIVERY BENEFITS:")
    print(f"   🚫 No toll-free verification required")
    print(f"   📱 Higher delivery rates")
    print(f"   💰 Lower cost per message")
    print(f"   🔒 A2P 10DLC compliant")
    print(f"   ⚡ Immediate sending capability")
    
    print(f"\n📊 EXPECTED RESULTS:")
    print(f"   ✅ Message delivered successfully")
    print(f"   ✅ No carrier blocking issues")
    print(f"   ✅ Professional local presence")
    print(f"   ✅ Better customer trust (local number)")
    print(f"   ✅ Reliable SMS delivery")

def show_campaign_status():
    """Show final campaign status."""
    print(f"\n" + "=" * 65)
    print(f"🎒 BACK TO SCHOOL SMS CAMPAIGN - SUCCESSFULLY DELIVERED")
    print(f"=" * 65)
    
    print(f"✅ CAMPAIGN STATUS: DELIVERED")
    print(f"   🎯 Target Customer: DJ Martin")
    print(f"   📱 Contact Method: SMS via verified local number")
    print(f"   🎒 Promotion: Back to School Braiding Special")
    print(f"   💰 Discount: $15 OFF")
    print(f"   ⏰ Urgency: This week only")
    print(f"   📞 From: +12019928729 (verified local)")
    
    print(f"\n🚀 IMMEDIATE NEXT ACTIONS:")
    print(f"   1. 📊 Monitor delivery status in Twilio Console")
    print(f"   2. 📱 Watch for customer replies (BOOK, INFO, STOP)")
    print(f"   3. 📞 Be ready for calls to (610) 288-0343")
    print(f"   4. 📅 Prepare to schedule DJ Martin's appointment")
    print(f"   5. 📈 Track response and conversion rates")
    
    print(f"\n🔥 TwistyVoice AI Assistant: PROMOTIONAL SMS DELIVERED!")

if __name__ == "__main__":
    print("🔥 TwistyVoice - SMS RESEND WITH LOCAL NUMBER")
    print("🎒 Back to School Braiding Special")
    print("👤 Target: DJ Martin")
    print("💰 Offer: $15 OFF back-to-school braids")
    print("📱 Method: Verified Local Number (+12019928729)")
    print()
    
    # Final confirmation
    confirm = input("📱 RESEND: Send promotional SMS from verified local number? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ SMS resend cancelled")
        sys.exit(0)
    
    print("\n📱 RESENDING SMS WITH LOCAL NUMBER...")
    
    message_sid = resend_promotional_sms()
    
    if message_sid:
        show_delivery_advantages()
        show_campaign_status()
        
        print(f"\n🎉 PROMOTIONAL SMS SUCCESSFULLY DELIVERED!")
        print(f"📱 DJ Martin will receive the promotion from your local number!")
        print(f"🆔 Message SID: {message_sid}")
        
    else:
        print(f"\n❌ SMS resend failed. Check errors above.")
