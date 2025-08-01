#!/usr/bin/env python3
"""
Test the complete promotional call workflow:
1. Trigger a promotional campaign
2. Test call handling and response processing
3. Test booking creation from call responses
4. Verify conversation tracking
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running and healthy."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_customer_data():
    """Test customer data endpoints."""
    print("\n📊 Testing Customer Data...")
    try:
        # Test getting customers
        response = requests.get(f"{BASE_URL}/api/v1/admin/customers")
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Found {len(customers)} customers in database")
            if customers:
                customer = customers[0]
                print(f"   Sample customer: {customer.get('first_name')} {customer.get('last_name')}")
                print(f"   Phone: {customer.get('phone_number')}")
                print(f"   Total visits: {customer.get('total_visits')}")
                return customer
        else:
            print(f"❌ Failed to get customers: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error testing customer data: {e}")
        return None

def test_promotional_campaign(customer_id=None):
    """Test triggering a promotional campaign."""
    print("\n📞 Testing Promotional Campaign...")
    try:
        if not customer_id:
            print("⚠️  No customer ID provided, skipping campaign test")
            return None

        # Test campaign start endpoint (the actual available endpoint)
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/campaigns/start?promotion_id=1",
            json=[customer_id]  # customer_ids as list in body
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Promotional campaign started successfully")
            print(f"   Campaign result: {result}")
            return result
        else:
            print(f"❌ Failed to start campaign: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing promotional campaign: {e}")
        return None

def test_twiml_generation(customer_id=None):
    """Test TwiML generation for promotional calls."""
    print("\n🎵 Testing TwiML Generation...")
    try:
        if not customer_id:
            print("⚠️  No customer ID provided, skipping TwiML test")
            return False

        # Test TwiML generation endpoint with required parameters
        response = requests.get(f"{BASE_URL}/api/v1/twiml/promotional_call?customer_id={customer_id}&promotion_id=1")

        if response.status_code == 200:
            twiml = response.text
            print("✅ TwiML generation working")
            print(f"   Generated TwiML length: {len(twiml)} characters")
            if "<Say" in twiml and "<Gather" in twiml:
                print("✅ TwiML contains expected elements (Say, Gather)")
                return True
            else:
                print("⚠️  TwiML missing expected elements")
                print(f"   TwiML preview: {twiml[:200]}...")
                return False
        else:
            print(f"❌ Failed to generate TwiML: {response.status_code}")
            if response.status_code == 422:
                print("⚠️  Parameter validation error")
            return False
    except Exception as e:
        print(f"❌ Error testing TwiML generation: {e}")
        return False

def test_call_response_handling():
    """Test call response handling."""
    print("\n📱 Testing Call Response Handling...")
    try:
        # Simulate customer pressing 1 (book appointment)
        response_data = {
            "Digits": "1",
            "CallSid": "test_call_123",
            "From": "+2566946682"  # DJ Martin's number
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/webhooks/gather_response",
            data=response_data
        )
        
        if response.status_code == 200:
            twiml = response.text
            print("✅ Call response handling working")
            print(f"   Response TwiML length: {len(twiml)} characters")
            if "book" in twiml.lower() or "appointment" in twiml.lower():
                print("✅ Response contains booking-related content")
                return True
            else:
                print("⚠️  Response doesn't contain expected booking content")
                return False
        else:
            print(f"❌ Failed to handle call response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing call response handling: {e}")
        return False

def test_conversation_tracking(customer_id=None):
    """Test conversation tracking."""
    print("\n💬 Testing Conversation Tracking...")
    try:
        if not customer_id:
            print("⚠️  No customer ID provided, skipping conversation test")
            return True

        # Test getting conversations for a specific customer
        response = requests.get(f"{BASE_URL}/api/v1/admin/customers/{customer_id}/conversations")

        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Found {len(conversations)} conversations for customer {customer_id}")
            if conversations:
                conv = conversations[0]
                print(f"   Sample conversation: {conv.get('call_sid')}")
                print(f"   Customer response: {conv.get('customer_response')}")
                return True
            else:
                print("⚠️  No conversations found (expected for fresh setup)")
                return True
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing conversation tracking: {e}")
        return False

def test_booking_endpoints():
    """Test booking-related endpoints."""
    print("\n📅 Testing Booking Endpoints...")
    try:
        # Test getting bookings
        response = requests.get(f"{BASE_URL}/api/v1/admin/bookings")
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"✅ Found {len(bookings)} bookings")
            if bookings:
                booking = bookings[0]
                print(f"   Sample booking: {booking.get('service_name')}")
                print(f"   Date: {booking.get('appointment_date')}")
                return True
            else:
                print("⚠️  No bookings found (expected for fresh setup)")
                return True
        else:
            print(f"❌ Failed to get bookings: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing booking endpoints: {e}")
        return False

def main():
    """Run all promotional workflow tests."""
    print("🚀 Testing TwistyVoice Promotional Workflow")
    print("=" * 60)
    
    # Test 1: API Health
    api_healthy = test_api_health()
    if not api_healthy:
        print("\n❌ API is not running. Please start the application first.")
        return
    
    # Test 2: Customer Data
    customer = test_customer_data()
    customer_id = customer.get('id') if customer else None

    # Test 3: Promotional Campaign
    campaign = test_promotional_campaign(customer_id)

    # Test 4: TwiML Generation
    twiml_working = test_twiml_generation(customer_id)

    # Test 5: Call Response Handling
    response_working = test_call_response_handling()

    # Test 6: Conversation Tracking
    conversation_working = test_conversation_tracking(customer_id)

    # Test 7: Booking Endpoints
    booking_working = test_booking_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Promotional Workflow Test Summary:")
    print(f"   API Health: {'✅' if api_healthy else '❌'}")
    print(f"   Customer Data: {'✅' if customer else '❌'}")
    print(f"   Promotional Campaign: {'✅' if campaign else '❌'}")
    print(f"   TwiML Generation: {'✅' if twiml_working else '❌'}")
    print(f"   Call Response Handling: {'✅' if response_working else '❌'}")
    print(f"   Conversation Tracking: {'✅' if conversation_working else '❌'}")
    print(f"   Booking Endpoints: {'✅' if booking_working else '❌'}")
    
    if all([api_healthy, customer, twiml_working, response_working]):
        print("\n🎉 Promotional workflow is ready!")
        print("\n📋 Next Steps:")
        print("   1. Configure real Twilio credentials for actual calls")
        print("   2. Configure ElevenLabs API key for AI voice generation")
        print("   3. Add more customer data to data/customers.csv")
        print("   4. Test with real phone calls using Twilio webhooks")
        print("\n💡 To test with real calls:")
        print("   - Set up Twilio webhook URLs pointing to your server")
        print("   - Use ngrok or similar for local development")
        print("   - Configure your Twilio phone number to use the webhooks")
    else:
        print("\n⚠️  Some components need attention before going live.")

if __name__ == "__main__":
    main()
