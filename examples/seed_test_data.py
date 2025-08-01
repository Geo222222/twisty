#!/usr/bin/env python3
"""
Script to seed test data for TwistyVoice application.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

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
env_backup = Path('.env.seed_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    from models.database import get_db, Promotion
    from sqlalchemy.orm import Session
    
    print("🌱 Seeding test data...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if promotions already exist
        existing_promotions = db.query(Promotion).count()
        print(f"📊 Found {existing_promotions} existing promotions")
        
        if existing_promotions == 0:
            # Create test promotions
            promotions = [
                Promotion(
                    name="Welcome Back Special",
                    description="20% off your next visit - we've missed you!",
                    discount_percentage=20.0,
                    target_services='["braids", "styling", "cuts"]',
                    target_customer_segments='["returning"]',
                    min_days_since_visit=30,
                    max_days_since_visit=365,
                    start_date=datetime.utcnow() - timedelta(days=1),
                    end_date=datetime.utcnow() + timedelta(days=30),
                    max_uses=100,
                    current_uses=0,
                    is_active=True
                ),
                Promotion(
                    name="New Style Discount",
                    description="Try something new! $15 off any new service",
                    discount_amount=15.0,
                    target_services='["styling", "color", "treatments"]',
                    target_customer_segments='["all"]',
                    min_days_since_visit=0,
                    max_days_since_visit=90,
                    start_date=datetime.utcnow() - timedelta(days=1),
                    end_date=datetime.utcnow() + timedelta(days=60),
                    max_uses=50,
                    current_uses=0,
                    is_active=True
                ),
                Promotion(
                    name="Back to School Braiding Special",
                    description="$15 OFF all back-to-school braids - Valid this week only!",
                    discount_amount=15.0,
                    target_services='["braids", "protective_styles", "back_to_school"]',
                    target_customer_segments='["lapsed", "vip", "returning"]',
                    min_days_since_visit=14,
                    max_days_since_visit=180,
                    start_date=datetime.utcnow() - timedelta(days=1),
                    end_date=datetime.utcnow() + timedelta(days=7),  # This week only
                    max_uses=25,
                    current_uses=0,
                    is_active=True
                )
            ]
            
            for promotion in promotions:
                db.add(promotion)
            
            db.commit()
            print(f"✅ Created {len(promotions)} test promotions")
            
            # List created promotions
            for promotion in promotions:
                print(f"   📢 {promotion.name}: {promotion.description}")
        else:
            print("✅ Promotions already exist, skipping creation")
            
        # Show all promotions
        all_promotions = db.query(Promotion).all()
        print(f"\n📋 All promotions in database:")
        for promotion in all_promotions:
            print(f"   ID {promotion.id}: {promotion.name}")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)

print("🎉 Test data seeding complete!")
