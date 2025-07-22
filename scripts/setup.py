#!/usr/bin/env python3
"""
Setup script for TwistyVoice AI Assistant

This script initializes the database and loads sample data.
"""

import sys
import os
from pathlib import Path
import yaml
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.database import create_tables, SessionLocal, Customer, Promotion
from config.settings import get_settings

def load_sample_promotions():
    """Load sample promotions from YAML file."""
    promotions_file = Path(__file__).parent.parent / "data" / "sample_promotions.yaml"
    
    if not promotions_file.exists():
        print(f"Sample promotions file not found: {promotions_file}")
        return
    
    with open(promotions_file, 'r') as f:
        data = yaml.safe_load(f)
    
    db = SessionLocal()
    
    try:
        for promo_data in data['promotions']:
            # Check if promotion already exists
            existing = db.query(Promotion).filter(
                Promotion.name == promo_data['name']
            ).first()
            
            if existing:
                print(f"Promotion '{promo_data['name']}' already exists, skipping...")
                continue
            
            # Convert lists to JSON strings
            if 'target_customer_segments' in promo_data:
                promo_data['target_customer_segments'] = json.dumps(
                    promo_data['target_customer_segments']
                )
            
            if 'target_services' in promo_data:
                promo_data['target_services'] = json.dumps(
                    promo_data['target_services']
                )
            
            # Create promotion
            promotion = Promotion(**promo_data)
            db.add(promotion)
            print(f"Added promotion: {promotion.name}")
        
        db.commit()
        print(f"Successfully loaded {len(data['promotions'])} promotions")
        
    except Exception as e:
        print(f"Error loading promotions: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_customers():
    """Create sample customers for testing."""
    sample_customers = [
        {
            "square_customer_id": "sample_customer_1",
            "first_name": "Alice",
            "last_name": "Johnson",
            "phone_number": "+15551234567",
            "email": "alice.johnson@example.com",
            "total_visits": 8,
            "total_spent": 480.0,
            "preferred_services": json.dumps(["braids", "styling"]),
            "visit_frequency": "monthly"
        },
        {
            "square_customer_id": "sample_customer_2", 
            "first_name": "Maria",
            "last_name": "Garcia",
            "phone_number": "+15551234568",
            "email": "maria.garcia@example.com",
            "total_visits": 15,
            "total_spent": 1200.0,
            "preferred_services": json.dumps(["color", "cut"]),
            "visit_frequency": "bi-weekly"
        },
        {
            "square_customer_id": "sample_customer_3",
            "first_name": "Sarah",
            "last_name": "Williams",
            "phone_number": "+15551234569",
            "email": "sarah.williams@example.com",
            "total_visits": 3,
            "total_spent": 180.0,
            "preferred_services": json.dumps(["cut", "styling"]),
            "visit_frequency": "quarterly"
        },
        {
            "square_customer_id": "sample_customer_4",
            "first_name": "Jennifer",
            "last_name": "Brown",
            "phone_number": "+15551234570",
            "email": "jennifer.brown@example.com",
            "total_visits": 0,
            "total_spent": 0.0,
            "preferred_services": json.dumps([]),
            "visit_frequency": "new"
        }
    ]
    
    db = SessionLocal()
    
    try:
        for customer_data in sample_customers:
            # Check if customer already exists
            existing = db.query(Customer).filter(
                Customer.square_customer_id == customer_data['square_customer_id']
            ).first()
            
            if existing:
                print(f"Customer '{customer_data['first_name']} {customer_data['last_name']}' already exists, skipping...")
                continue
            
            customer = Customer(**customer_data)
            db.add(customer)
            print(f"Added customer: {customer.first_name} {customer.last_name}")
        
        db.commit()
        print(f"Successfully created {len(sample_customers)} sample customers")
        
    except Exception as e:
        print(f"Error creating sample customers: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main setup function."""
    print("🌟 Setting up TwistyVoice AI Assistant...")
    
    # Load settings
    settings = get_settings()
    print(f"Using database: {settings.DATABASE_URL}")
    
    # Create database tables
    print("Creating database tables...")
    create_tables()
    print("✅ Database tables created")
    
    # Load sample promotions
    print("Loading sample promotions...")
    load_sample_promotions()
    print("✅ Sample promotions loaded")
    
    # Create sample customers
    print("Creating sample customers...")
    create_sample_customers()
    print("✅ Sample customers created")
    
    print("\n🎉 TwistyVoice setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Run: python -m src.main")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("\nFor production deployment:")
    print("1. Configure your production environment variables")
    print("2. Run: docker-compose up -d")


if __name__ == "__main__":
    main()
