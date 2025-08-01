#!/usr/bin/env python3
"""
Test script to check if routes can be imported properly.
"""

import os
import sys
from pathlib import Path

# Set up environment variables before importing anything
os.environ.update({
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'SQUARE_APPLICATION_ID': 'test',
    'SQUARE_ACCESS_TOKEN': 'test',
    'TWILIO_ACCOUNT_SID': 'test',
    'TWILIO_AUTH_TOKEN': 'test',
    'TWILIO_PHONE_NUMBER': 'test',
    'ELEVENLABS_API_KEY': 'test',
    'SMTP_USERNAME': 'test',
    'SMTP_PASSWORD': 'test',
    'MANAGER_EMAIL': 'test@test.com',
    'SALON_PHONE': 'test',
    'SALON_ADDRESS': 'test',
    'SECRET_KEY': 'test',
    'ENCRYPTION_KEY': 'test' * 8  # 32 characters
})

# Temporarily move .env file
env_file = Path('.env')
env_backup = Path('.env.routes_test_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    print("🔍 Testing routes import...")
    
    # Test importing dependencies first
    try:
        print("🔍 Testing individual imports...")

        from models.database import get_db, Customer, Conversation, Booking, Promotion
        print("✅ Database models imported")

        from core.voice_agent import VoiceAgent
        print("✅ VoiceAgent imported")

        from core.conversation_tracker import ConversationTracker
        print("✅ ConversationTracker imported")

        from core.booking_handler import BookingHandler
        print("✅ BookingHandler imported")

        from core.promotion_engine import PromotionEngine
        print("✅ PromotionEngine imported")

        from core.report_generator import ReportGenerator
        print("✅ ReportGenerator imported")

        from config.settings import get_settings
        print("✅ Settings imported")

    except Exception as e:
        print(f"❌ Error importing dependencies: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

    # Test importing routes
    try:
        from api.routes import api_router, webhooks_router, admin_router, twiml_router
        print("✅ Successfully imported routers")

        # Check if routes are registered
        print(f"✅ api_router has {len(api_router.routes)} routes")
        print(f"✅ webhooks_router has {len(webhooks_router.routes)} routes")
        print(f"✅ admin_router has {len(admin_router.routes)} routes")
        print(f"✅ twiml_router has {len(twiml_router.routes)} routes")

        # List all routes
        for router_name, router in [("webhooks", webhooks_router), ("admin", admin_router), ("twiml", twiml_router)]:
            for route in router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    print(f"   {router_name}: {route.methods} {route.path}")

    except Exception as e:
        print(f"❌ Error importing routes: {e}")
        import traceback
        traceback.print_exc()
    
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)
