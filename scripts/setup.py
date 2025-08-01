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
import csv

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


def load_customers_from_csv():
    """Load customers from CSV file."""
    csv_file = Path(__file__).parent.parent / "data" / "customers.csv"
    
    if not csv_file.exists():
        print(f"Customer CSV file not found: {csv_file}")
        print("Please create a customers.csv file in the data/ directory with your customer data.")
        print("See data/customers.csv for the expected format.")
        return
    
    db = SessionLocal()
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check if customer already exists by phone or email
                existing = db.query(Customer).filter(
                    (Customer.phone_number == row.get('phone_number')) |
                    (Customer.email == row.get('email'))
                ).first()
                
                if existing:
                    print(f"Customer '{row['first_name']} {row['last_name']}' already exists, skipping...")
                    continue
                
                # Prepare customer data
                customer_data = {
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone_number': row.get('phone_number', ''),
                    'email': row.get('email', ''),
                    'total_visits': int(row.get('total_visits', 0)),
                    'total_spent': float(row.get('total_spent', 0.0)),
                    'visit_frequency': row.get('visit_frequency', 'monthly'),
                    'preferred_stylist': row.get('preferred_stylist', ''),
                    'preferred_services': json.dumps(row.get('preferred_services', '').split(',') if row.get('preferred_services') else []),
                    'opt_out_calls': row.get('opt_out_calls', '').lower() == 'true',
                    'opt_out_sms': row.get('opt_out_sms', '').lower() == 'true',
                    'preferred_contact_time': row.get('preferred_contact_time', 'afternoon')
                }
                
                customer = Customer(**customer_data)
                db.add(customer)
                print(f"Added customer: {customer.first_name} {customer.last_name}")
        
        db.commit()
        print("✅ Successfully loaded customers from CSV")
        
    except Exception as e:
        print(f"Error loading customers from CSV: {e}")
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
    
    # Load customers from CSV
    print("Loading customers from CSV...")
    load_customers_from_csv()
    print("✅ Customers loaded from CSV")
    
    print("\n🎉 TwistyVoice setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Edit data/customers.csv to add your actual customer data")
    print("3. Run: python -m src.main")
    print("4. Visit http://localhost:8000/docs for API documentation")
    print("\nFor production deployment:")
    print("1. Configure your production environment variables")
    print("2. Run: docker-compose up -d")


if __name__ == "__main__":
    main()
