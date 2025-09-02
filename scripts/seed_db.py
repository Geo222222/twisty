#!/usr/bin/env python3
"""
Database seeding script for TwistyVoice portfolio demo.

This script creates and populates the SQLite database with realistic sample data
for demonstration purposes. No external API calls are made.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.database import (
    engine, Base, SessionLocal,
    Tenant, Customer, Promotion, Conversation, Booking, CallCampaign
)
from config.settings import get_settings

settings = get_settings()


def create_tables():
    """Create all database tables."""
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def seed_tenants(db):
    """Seed the database with sample tenant."""
    print("🏢 Seeding tenant...")

    tenant_data = {
        "id": 1,
        "name": "GetTwisted Hair Studios",
        "slug": "gettwisted"
    }

    # Check if tenant already exists
    existing_tenant = db.query(Tenant).filter(Tenant.id == 1).first()
    if not existing_tenant:
        tenant = Tenant(**tenant_data)
        db.add(tenant)
        db.commit()
        print("✅ Seeded default tenant")
    else:
        print("✅ Default tenant already exists")


def seed_customers(db):
    """Seed the database with sample customers."""
    print("👥 Seeding customers...")
    
    customers_data = [
        {
            "first_name": "Sarah",
            "last_name": "Johnson", 
            "phone_number": "+15551234567",
            "email": "sarah.johnson@email.com",
            "preferred_stylist": "Maria",
            "preferred_services": '["Haircut", "Color", "Highlights"]',
            "visit_frequency": "monthly",
            "last_visit_date": datetime.utcnow() - timedelta(days=45),
            "total_visits": 12,
            "total_spent": 1800.0,
            "opt_out_calls": False,
            "opt_out_sms": False,
            "preferred_contact_time": "afternoon"
        },
        {
            "first_name": "Emily",
            "last_name": "Davis",
            "phone_number": "+15551234568", 
            "email": "emily.davis@email.com",
            "preferred_stylist": "Jessica",
            "preferred_services": '["Haircut", "Blowout"]',
            "visit_frequency": "bi-weekly",
            "last_visit_date": datetime.utcnow() - timedelta(days=20),
            "total_visits": 24,
            "total_spent": 2400.0,
            "opt_out_calls": False,
            "opt_out_sms": False,
            "preferred_contact_time": "morning"
        },
        {
            "first_name": "Ashley",
            "last_name": "Wilson",
            "phone_number": "+15551234569",
            "email": "ashley.wilson@email.com",
            "preferred_stylist": "Maria",
            "preferred_services": '["Haircut", "Color", "Treatment"]',
            "visit_frequency": "weekly",
            "last_visit_date": datetime.utcnow() - timedelta(days=10),
            "total_visits": 48,
            "total_spent": 4800.0,
            "opt_out_calls": False,
            "opt_out_sms": False,
            "preferred_contact_time": "evening"
        },
        {
            "first_name": "Jennifer",
            "last_name": "Brown",
            "phone_number": "+15551234570",
            "email": "jennifer.brown@email.com",
            "preferred_stylist": "Any",
            "preferred_services": '["Haircut"]',
            "visit_frequency": "quarterly",
            "last_visit_date": datetime.utcnow() - timedelta(days=120),
            "total_visits": 4,
            "total_spent": 320.0,
            "opt_out_calls": False,
            "opt_out_sms": False,
            "preferred_contact_time": "afternoon"
        },
        {
            "first_name": "Michelle",
            "last_name": "Taylor",
            "phone_number": "+15551234571",
            "email": "michelle.taylor@email.com",
            "preferred_stylist": "Jessica",
            "preferred_services": '["Haircut", "Color"]',
            "visit_frequency": "monthly",
            "last_visit_date": datetime.utcnow() - timedelta(days=35),
            "total_visits": 8,
            "total_spent": 960.0,
            "opt_out_calls": False,
            "opt_out_sms": False,
            "preferred_contact_time": "morning"
        }
    ]
    
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
    
    db.commit()
    print(f"✅ Seeded {len(customers_data)} customers")


def seed_promotions(db):
    """Seed the database with sample promotions."""
    print("🎯 Seeding promotions...")
    
    promotions_data = [
        {
            "name": "Back to School Special",
            "description": "20% off haircuts for students and teachers",
            "discount_percentage": 20.0,
            "target_services": '["Haircut"]',
            "target_customer_segments": '["students", "teachers"]',
            "min_days_since_visit": 30,
            "max_days_since_visit": 90,
            "start_date": datetime.utcnow() - timedelta(days=7),
            "end_date": datetime.utcnow() + timedelta(days=23),
            "max_uses": 50,
            "current_uses": 12,
            "is_active": True
        },
        {
            "name": "VIP Customer Appreciation",
            "description": "Complimentary deep conditioning treatment for VIP customers",
            "discount_amount": 45.0,
            "target_services": '["Treatment", "Deep Conditioning"]',
            "target_customer_segments": '["vip"]',
            "min_days_since_visit": 14,
            "max_days_since_visit": 60,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "max_uses": 25,
            "current_uses": 3,
            "is_active": True
        },
        {
            "name": "New Client Welcome",
            "description": "50% off first visit for new clients",
            "discount_percentage": 50.0,
            "target_services": '["Haircut", "Color", "Blowout"]',
            "target_customer_segments": '["new"]',
            "min_days_since_visit": 0,
            "max_days_since_visit": 0,
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow() + timedelta(days=60),
            "max_uses": 100,
            "current_uses": 8,
            "is_active": True
        }
    ]
    
    for promo_data in promotions_data:
        promotion = Promotion(**promo_data)
        db.add(promotion)
    
    db.commit()
    print(f"✅ Seeded {len(promotions_data)} promotions")


def seed_conversations(db):
    """Seed the database with sample conversation history."""
    print("💬 Seeding conversation history...")
    
    # Get customers and promotions for relationships
    customers = db.query(Customer).all()
    promotions = db.query(Promotion).all()
    
    conversations_data = [
        {
            "customer_id": customers[0].id,
            "promotion_id": promotions[0].id,
            "call_type": "promotional",
            "call_status": "answered",
            "call_duration": 120,
            "customer_response": "interested",
            "notes": "Customer interested in back to school special, will call back to book",
            "follow_up_required": True,
            "follow_up_date": datetime.utcnow() + timedelta(days=2),
            "twilio_call_sid": "CA1234567890abcdef1234567890abcdef",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "customer_id": customers[1].id,
            "promotion_id": promotions[1].id,
            "call_type": "promotional",
            "call_status": "voicemail",
            "call_duration": 0,
            "customer_response": "no_response",
            "notes": "Left voicemail about VIP appreciation offer",
            "follow_up_required": True,
            "follow_up_date": datetime.utcnow() + timedelta(days=1),
            "twilio_call_sid": "CA1234567890abcdef1234567890abcde1",
            "created_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "customer_id": customers[2].id,
            "promotion_id": promotions[1].id,
            "call_type": "promotional",
            "call_status": "answered",
            "call_duration": 180,
            "customer_response": "booked",
            "notes": "Customer booked appointment for VIP treatment",
            "follow_up_required": False,
            "twilio_call_sid": "CA1234567890abcdef1234567890abcde2",
            "created_at": datetime.utcnow() - timedelta(hours=24)
        }
    ]
    
    for conv_data in conversations_data:
        conversation = Conversation(**conv_data)
        db.add(conversation)
    
    db.commit()
    print(f"✅ Seeded {len(conversations_data)} conversation records")


def seed_bookings(db):
    """Seed the database with sample bookings."""
    print("📅 Seeding bookings...")
    
    customers = db.query(Customer).all()
    conversations = db.query(Conversation).all()
    
    bookings_data = [
        {
            "customer_id": customers[2].id,
            "conversation_id": conversations[2].id,
            "external_booking_id": "SQ_BOOK_001",
            "appointment_datetime": datetime.utcnow() + timedelta(days=3, hours=10),
            "service_name": "VIP Deep Conditioning Treatment",
            "stylist_name": "Maria",
            "duration_minutes": 90,
            "price": 45.0,
            "status": "confirmed",
            "created_via": "voice_call"
        },
        {
            "customer_id": customers[0].id,
            "external_booking_id": "SQ_BOOK_002", 
            "appointment_datetime": datetime.utcnow() + timedelta(days=5, hours=14),
            "service_name": "Haircut and Highlights",
            "stylist_name": "Maria",
            "duration_minutes": 120,
            "price": 120.0,
            "status": "confirmed",
            "created_via": "manual"
        }
    ]
    
    for booking_data in bookings_data:
        booking = Booking(**booking_data)
        db.add(booking)
    
    db.commit()
    print(f"✅ Seeded {len(bookings_data)} bookings")


def main():
    """Main seeding function."""
    print("🌱 Starting database seeding for TwistyVoice demo...")
    print(f"📍 Database: {settings.DATABASE_URL}")
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data for clean demo
        print("🧹 Clearing existing data...")
        db.query(Booking).delete()
        db.query(Conversation).delete()
        db.query(CallCampaign).delete()
        db.query(Promotion).delete()
        db.query(Customer).delete()
        db.commit()

        # Seed all data
        seed_tenants(db)
        seed_customers(db)
        seed_promotions(db)
        seed_conversations(db)
        seed_bookings(db)
        
        print("\n🎉 Database seeding completed successfully!")
        print("📊 Demo data summary:")
        print(f"   • {db.query(Customer).count()} customers")
        print(f"   • {db.query(Promotion).count()} active promotions")
        print(f"   • {db.query(Conversation).count()} conversation records")
        print(f"   • {db.query(Booking).count()} bookings")
        print("\n✨ Ready for demo! Run 'make serve' to start the API server.")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
