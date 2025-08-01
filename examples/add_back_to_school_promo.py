#!/usr/bin/env python3
"""
Script to add the Back to School Braiding Special promotion.
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
env_backup = Path('.env.promo_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    from models.database import get_db, Promotion
    from sqlalchemy.orm import Session
    
    print("🎒 Adding Back to School Braiding Special...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if this specific promotion already exists
        existing_promo = db.query(Promotion).filter(
            Promotion.name == "Back to School Braiding Special"
        ).first()
        
        if existing_promo:
            print("✅ Back to School Braiding Special already exists!")
            print(f"   ID: {existing_promo.id}")
            print(f"   Description: {existing_promo.description}")
        else:
            # Create the Back to School promotion
            back_to_school_promo = Promotion(
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
            
            db.add(back_to_school_promo)
            db.commit()
            
            print("✅ Created Back to School Braiding Special!")
            print(f"   ID: {back_to_school_promo.id}")
            print(f"   Description: {back_to_school_promo.description}")
            print(f"   Discount: ${back_to_school_promo.discount_amount}")
            print(f"   Valid until: {back_to_school_promo.end_date.strftime('%Y-%m-%d')}")
            
        # Show all promotions
        all_promotions = db.query(Promotion).all()
        print(f"\n📋 All promotions in database:")
        for promotion in all_promotions:
            status = "🟢 ACTIVE" if promotion.is_active else "🔴 INACTIVE"
            print(f"   ID {promotion.id}: {promotion.name} {status}")
            
    except Exception as e:
        print(f"❌ Error adding promotion: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)

print("🎉 Back to School promotion ready!")
