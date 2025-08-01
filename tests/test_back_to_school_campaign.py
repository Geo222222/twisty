#!/usr/bin/env python3
"""
Test script for Back to School Braiding Special campaign.
This will execute a real promotional call to DJ Martin.
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"

def test_back_to_school_campaign():
    """Execute the Back to School Braiding Special campaign."""
    
    print("🎒 BACK TO SCHOOL BRAIDING SPECIAL - LIVE TEST")
    print("=" * 60)
    
    # Step 1: Verify API is running
    print("🔍 Checking API status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ TwistyVoice API is running")
        else:
            print(f"❌ API not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Step 2: Get customer data (DJ Martin)
    print("\n📊 Getting customer data...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/customers")
        if response.status_code == 200:
            customers = response.json()
            if customers:
                customer = customers[0]  # DJ Martin should be first
                customer_id = customer['id']
                customer_name = f"{customer['first_name']} {customer['last_name']}"
                print(f"✅ Target customer: {customer_name}")
                print(f"   Phone: {customer['phone_number']}")
                print(f"   Total visits: {customer['total_visits']}")
            else:
                print("❌ No customers found")
                return False
        else:
            print(f"❌ Failed to get customers: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting customers: {e}")
        return False
    
    # Step 3: Verify Back to School promotion exists
    print("\n🎯 Verifying Back to School promotion...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/promotions")
        if response.status_code == 200:
            promotions = response.json()
            back_to_school_promo = None
            for promo in promotions:
                if "Back to School" in promo['name']:
                    back_to_school_promo = promo
                    break
            
            if back_to_school_promo:
                promotion_id = back_to_school_promo['id']
                print(f"✅ Found promotion: {back_to_school_promo['name']}")
                print(f"   ID: {promotion_id}")
                print(f"   Discount: ${back_to_school_promo['discount_amount']}")
            else:
                print("❌ Back to School promotion not found")
                return False
        else:
            print(f"❌ Failed to get promotions: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting promotions: {e}")
        return False
    
    # Step 4: Test TwiML generation for this specific campaign
    print("\n🎵 Testing campaign TwiML generation...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/twiml/promotional_call",
            params={
                "customer_id": customer_id,
                "promotion_id": promotion_id
            }
        )
        
        if response.status_code == 200:
            twiml = response.text
            print("✅ TwiML generated successfully")
            print(f"   Length: {len(twiml)} characters")
            
            # Show preview of the voice script
            if "Back to School" in twiml:
                print("✅ Contains Back to School messaging")
            if "$15" in twiml or "15" in twiml:
                print("✅ Contains discount amount")
            if "press 1" in twiml.lower():
                print("✅ Contains booking prompt")
                
            print(f"\n📝 TwiML Preview:")
            print("-" * 40)
            # Extract and clean the Say content for preview
            import re
            say_matches = re.findall(r'<Say[^>]*>(.*?)</Say>', twiml, re.DOTALL)
            for i, say_content in enumerate(say_matches[:2]):  # Show first 2 Say elements
                clean_content = say_content.strip()
                print(f"Voice Message {i+1}: {clean_content}")
            print("-" * 40)
            
        else:
            print(f"❌ Failed to generate TwiML: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing TwiML: {e}")
        return False
    
    # Step 5: Execute the campaign
    print(f"\n🚀 EXECUTING BACK TO SCHOOL CAMPAIGN")
    print(f"   Target: {customer_name} ({customer['phone_number']})")
    print(f"   Promotion: {back_to_school_promo['name']}")
    print(f"   Discount: ${back_to_school_promo['discount_amount']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/campaigns/start",
            params={"promotion_id": promotion_id},
            json=[customer_id]
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CAMPAIGN STARTED SUCCESSFULLY!")
            print(f"   Campaign ID: {result['campaign_id']}")
            print(f"   Message: {result['message']}")
            
            # Log the campaign execution
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n📋 Campaign Log Entry:")
            print(f"   Timestamp: {timestamp}")
            print(f"   Customer: {customer_name} ({customer_id})")
            print(f"   Phone: {customer['phone_number']}")
            print(f"   Promotion: {back_to_school_promo['name']} (ID: {promotion_id})")
            print(f"   Campaign ID: {result['campaign_id']}")
            
            return True
        else:
            print(f"❌ Failed to start campaign: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting campaign: {e}")
        return False

def show_next_steps():
    """Show next steps for monitoring the campaign."""
    print("\n" + "=" * 60)
    print("🎯 CAMPAIGN EXECUTED - NEXT STEPS")
    print("=" * 60)
    print("📞 CALL MONITORING:")
    print("   - Check Twilio console for call logs")
    print("   - Monitor webhook responses")
    print("   - Track customer responses (press 1 for booking)")
    print()
    print("📊 RESPONSE TRACKING:")
    print("   - GET /api/v1/admin/customers/1/conversations")
    print("   - GET /api/v1/admin/bookings")
    print("   - Monitor call response webhooks")
    print()
    print("🔧 REAL INTEGRATION:")
    print("   - Configure real Twilio credentials in .env")
    print("   - Set up ElevenLabs API key for AI voice")
    print("   - Configure webhook URLs (use ngrok for local testing)")
    print()
    print("💡 TEST RESPONSES:")
    print("   - Simulate customer pressing 1: POST /api/v1/webhooks/gather_response")
    print("   - Check booking creation and conversation logging")

if __name__ == "__main__":
    print("🔥 TwistyVoice - Back to School Campaign Test")
    print("🎯 Ready to execute promotional call to DJ Martin")
    print()
    
    success = test_back_to_school_campaign()
    
    if success:
        show_next_steps()
        print("\n🎉 BACK TO SCHOOL CAMPAIGN IS LIVE!")
    else:
        print("\n❌ Campaign execution failed. Check the errors above.")
