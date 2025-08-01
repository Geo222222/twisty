#!/usr/bin/env python3
"""
Test script to verify the complete TwistyVoice workflow:
1. Load customer data from CSV
2. Test promotion engine
3. Test voice agent with ElevenLabs
4. Test Twilio integration
5. Test booking functionality
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Temporarily move .env file to avoid conflicts
env_file = Path('.env')
env_backup = Path('.env.test_backup')

if env_file.exists():
    env_file.rename(env_backup)

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up test environment variables
os.environ.update({
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'SQUARE_APPLICATION_ID': 'test',
    'SQUARE_ACCESS_TOKEN': 'test',
    'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID', 'test'),
    'TWILIO_AUTH_TOKEN': os.getenv('TWILIO_AUTH_TOKEN', 'test'),
    'TWILIO_PHONE_NUMBER': os.getenv('TWILIO_PHONE_NUMBER', 'test'),
    'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY', 'test'),
    'SMTP_USERNAME': 'test',
    'SMTP_PASSWORD': 'test',
    'MANAGER_EMAIL': 'test@test.com',
    'SALON_PHONE': 'test',
    'SALON_ADDRESS': 'test',
    'SECRET_KEY': 'test',
    'ENCRYPTION_KEY': 'test' * 8  # 32 characters
})

from models.database import SessionLocal, Customer, Promotion
from core.promotion_engine import PromotionEngine, CustomerSegment
from core.voice_agent import VoiceAgent
from core.csv_data_connector import CSVDataConnector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_csv_data_loading():
    """Test loading customer data from CSV."""
    print("\n=== Testing CSV Data Loading ===")
    
    csv_connector = CSVDataConnector()
    
    # Test getting customer by phone
    customer = await csv_connector.get_customer_by_phone("+2566946682")
    if customer:
        print(f"✅ Found customer: {customer.first_name} {customer.last_name}")
        print(f"   Phone: {customer.phone_number}")
        print(f"   Total visits: {customer.total_visits}")
        print(f"   Total spent: ${customer.total_spent}")
        print(f"   Preferred services: {customer.preferred_services}")
        return customer
    else:
        print("❌ No customer found in CSV")
        return None


async def test_promotion_engine():
    """Test the promotion engine functionality."""
    print("\n=== Testing Promotion Engine ===")
    
    db = SessionLocal()
    try:
        # Get a customer from database
        customer = db.query(Customer).first()
        if not customer:
            print("❌ No customers in database. Run setup script first.")
            return None
        
        print(f"Testing with customer: {customer.first_name} {customer.last_name}")
        
        # Test promotion engine
        promotion_engine = PromotionEngine(db)
        
        # Analyze customer segment
        segments = promotion_engine.analyze_customer_segment(customer)
        print(f"✅ Customer segments: {segments}")
        
        # Get eligible promotions
        eligible_promotions = promotion_engine.get_eligible_promotions(customer)
        print(f"✅ Eligible promotions: {len(eligible_promotions)}")
        
        if eligible_promotions:
            best_promotion = promotion_engine.select_best_promotion(customer, eligible_promotions)
            if best_promotion:
                print(f"✅ Best promotion: {best_promotion.name}")
                return customer, best_promotion
        
        return customer, None
        
    except Exception as e:
        print(f"❌ Error testing promotion engine: {e}")
        return None, None
    finally:
        db.close()


async def test_voice_agent():
    """Test the voice agent with ElevenLabs."""
    print("\n=== Testing Voice Agent ===")

    try:
        voice_agent = VoiceAgent()

        # Create test customer and promotion for TwiML generation
        from models.database import SessionLocal
        db = SessionLocal()
        try:
            customer = db.query(Customer).first()
            promotion = db.query(Promotion).first()

            if customer and promotion:
                # Test TwiML generation
                twiml = voice_agent.generate_promotional_twiml(customer, promotion)

                if twiml and "<Say>" in twiml:
                    print("✅ TwiML generation working")
                    print(f"   Generated TwiML length: {len(twiml)} characters")
                else:
                    print("❌ TwiML generation failed")
            else:
                print("⚠️  No customer or promotion data for TwiML test")
        finally:
            db.close()

        # Test if ElevenLabs is configured
        if os.getenv('ELEVENLABS_API_KEY') and os.getenv('ELEVENLABS_API_KEY') != 'test':
            print("✅ ElevenLabs API key configured")
            # Could test actual voice generation here if needed
        else:
            print("⚠️  ElevenLabs API key not configured (using fallback)")

        return True

    except Exception as e:
        print(f"❌ Error testing voice agent: {e}")
        return False


async def test_twilio_integration():
    """Test Twilio integration."""
    print("\n=== Testing Twilio Integration ===")
    
    try:
        # Check if real Twilio credentials are configured
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if twilio_sid and twilio_token and twilio_phone and \
           twilio_sid != 'test' and twilio_token != 'test' and twilio_phone != 'test':
            print("✅ Twilio credentials configured")
            print(f"   Account SID: {twilio_sid[:8]}...")
            print(f"   Phone number: {twilio_phone}")
            
            # Could test actual Twilio connection here if needed
            return True
        else:
            print("⚠️  Twilio credentials not configured (using test values)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Twilio: {e}")
        return False


async def test_booking_functionality():
    """Test booking functionality."""
    print("\n=== Testing Booking Functionality ===")

    try:
        csv_connector = CSVDataConnector()

        # Test creating a booking
        booking_data = {
            "customer_id": "1",
            "service_name": "Hair Cut & Style",
            "stylist_name": "Tanya",
            "appointment_date": "2024-08-15",
            "appointment_time": "14:00",
            "duration_minutes": 90
        }

        booking_id = await csv_connector.create_booking(booking_data)

        if booking_id:
            print(f"✅ Booking created successfully: {booking_id}")

            # Test retrieving bookings
            bookings = await csv_connector.get_bookings()
            print(f"✅ Total bookings in system: {len(bookings)}")
            return True
        else:
            print("❌ Failed to create booking")
            return False

    except Exception as e:
        print(f"❌ Error testing booking functionality: {e}")
        return False


async def main():
    """Run all tests."""
    try:
        print("🚀 Starting TwistyVoice Workflow Tests")
        print("=" * 50)

        # Test 1: CSV Data Loading
        csv_customer = await test_csv_data_loading()

        # Test 2: Promotion Engine
        promotion_result = await test_promotion_engine()
        if promotion_result:
            db_customer, best_promotion = promotion_result
        else:
            db_customer, best_promotion = None, None

        # Test 3: Voice Agent
        voice_working = await test_voice_agent()

        # Test 4: Twilio Integration
        twilio_working = await test_twilio_integration()

        # Test 5: Booking Functionality
        booking_working = await test_booking_functionality()

        # Summary
        print("\n" + "=" * 50)
        print("🎯 Test Summary:")
        print(f"   CSV Data Loading: {'✅' if csv_customer else '❌'}")
        print(f"   Promotion Engine: {'✅' if db_customer and best_promotion else '⚠️' if db_customer else '❌'}")
        print(f"   Voice Agent: {'✅' if voice_working else '❌'}")
        print(f"   Twilio Integration: {'✅' if twilio_working else '⚠️'}")
        print(f"   Booking Functionality: {'✅' if booking_working else '❌'}")

        if csv_customer and db_customer and voice_working:
            print("\n🎉 Core functionality is working! Ready for promotional calls.")
        else:
            print("\n⚠️  Some components need attention before running promotional calls.")

    finally:
        # Restore .env file
        if env_backup.exists():
            env_backup.rename(env_file)


if __name__ == "__main__":
    asyncio.run(main())
