#!/usr/bin/env python3
"""
Demo campaign script for TwistyVoice portfolio demonstration.

This script demonstrates the complete promotional campaign workflow:
1. Query VIP customers from the seeded database
2. Send fake SMS campaigns using mock Twilio
3. Make fake voice calls using mock providers
4. Display results in a professional format

No external API calls are made - everything uses fake providers.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

from models.database import SessionLocal, Customer, Promotion, Conversation
from sdk_fakes.twilio_fake import get_twilio_client
from sdk_fakes.square_fake import get_square_client
from config.settings import get_settings

settings = get_settings()


def print_header():
    """Print demo header."""
    print("=" * 60)
    print("🎬 TwistyVoice AI Assistant - Portfolio Demo")
    print("=" * 60)
    print("📱 Salon Customer Engagement Campaign")
    print("🎭 Using FAKE providers (no real API calls)")
    print("-" * 60)


def get_vip_customers(db):
    """Query VIP customers who haven't visited recently."""
    print("🔍 Querying VIP customers from database...")
    
    # Define VIP criteria: customers with high visit frequency or high spending
    vip_customers = db.query(Customer).filter(
        (Customer.total_spent > 1000) |
        (Customer.visit_frequency.in_(["weekly", "bi-weekly", "monthly"]))
    ).filter(
        Customer.opt_out_calls == False,
        Customer.opt_out_sms == False
    ).all()
    
    print(f"📊 Found {len(vip_customers)} VIP customers eligible for campaign")
    
    for customer in vip_customers:
        days_since_visit = (datetime.utcnow() - customer.last_visit_date).days if customer.last_visit_date else 999
        print(f"   • {customer.first_name} {customer.last_name} - {days_since_visit} days since last visit")
    
    return vip_customers


def get_active_promotions(db):
    """Get currently active promotions."""
    print("\n🎯 Fetching active promotions...")
    
    now = datetime.utcnow()
    active_promotions = db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
        Promotion.current_uses < Promotion.max_uses
    ).all()
    
    print(f"📋 Found {len(active_promotions)} active promotions:")
    for promo in active_promotions:
        print(f"   • {promo.name}: {promo.description}")
    
    return active_promotions


def send_sms_campaign(customers, promotion):
    """Send SMS campaign using fake Twilio client."""
    print(f"\n📱 Sending SMS campaign: '{promotion.name}'")
    print("-" * 40)
    
    # Initialize fake Twilio client
    twilio_client = get_twilio_client()
    
    sms_results = []
    
    for customer in customers:
        # Create personalized message
        message_body = f"""Hi {customer.first_name}! 🌟

{promotion.description}

Book your appointment today at GetTwisted Hair Studios!
Call us: {settings.SALON_PHONE}

Reply STOP to opt out."""
        
        # Send fake SMS
        try:
            message = twilio_client.messages.create(
                to=customer.phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=message_body
            )
            
            result = {
                "customer": f"{customer.first_name} {customer.last_name}",
                "phone": customer.phone_number,
                "status": message.status,
                "message_sid": message.sid
            }
            sms_results.append(result)
            
            print(f"✅ {customer.first_name} {customer.last_name} ({customer.phone_number}): {message.status}")
            
        except Exception as e:
            print(f"❌ Failed to send SMS to {customer.first_name}: {e}")
    
    return sms_results


def make_voice_calls(customers, promotion):
    """Make voice calls using fake Twilio client."""
    print(f"\n📞 Making voice calls for: '{promotion.name}'")
    print("-" * 40)
    
    # Initialize fake Twilio client
    twilio_client = get_twilio_client()
    
    call_results = []
    
    for customer in customers[:3]:  # Limit to first 3 for demo
        # Create TwiML URL (would be real in production)
        twiml_url = f"https://twistyvoice.herokuapp.com/twiml/promotion/{promotion.id}"
        
        try:
            call = twilio_client.calls.create(
                to=customer.phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                url=twiml_url
            )
            
            result = {
                "customer": f"{customer.first_name} {customer.last_name}",
                "phone": customer.phone_number,
                "status": call.status,
                "duration": call.duration,
                "call_sid": call.sid
            }
            call_results.append(result)
            
            status_emoji = "✅" if call.status == "completed" else "⚠️"
            duration_text = f"({call.duration}s)" if call.duration else ""
            print(f"{status_emoji} {customer.first_name} {customer.last_name} ({customer.phone_number}): {call.status} {duration_text}")
            
        except Exception as e:
            print(f"❌ Failed to call {customer.first_name}: {e}")
    
    return call_results


def log_campaign_results(db, customers, promotion, sms_results, call_results):
    """Log campaign results to database."""
    print(f"\n📝 Logging campaign results to database...")
    
    for customer in customers:
        # Find SMS result for this customer
        sms_result = next((r for r in sms_results if customer.phone_number in r["phone"]), None)
        call_result = next((r for r in call_results if customer.phone_number in r["phone"]), None)
        
        # Create conversation record
        conversation = Conversation(
            customer_id=customer.id,
            promotion_id=promotion.id,
            call_type="promotional",
            call_status=call_result["status"] if call_result else "sms_only",
            call_duration=call_result["duration"] if call_result and call_result["duration"] else 0,
            customer_response="pending",
            notes=f"Campaign: {promotion.name}. SMS: {sms_result['status'] if sms_result else 'not_sent'}",
            follow_up_required=True,
            follow_up_date=datetime.utcnow() + timedelta(days=2),
            twilio_call_sid=call_result["call_sid"] if call_result else None
        )
        
        db.add(conversation)
    
    db.commit()
    print(f"✅ Logged {len(customers)} conversation records")


def display_campaign_summary(customers, promotion, sms_results, call_results):
    """Display professional campaign summary."""
    print("\n" + "=" * 60)
    print("📊 CAMPAIGN SUMMARY REPORT")
    print("=" * 60)
    
    print(f"🎯 Promotion: {promotion.name}")
    print(f"📅 Campaign Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    print(f"👥 Target Customers: {len(customers)}")
    
    print(f"\n📱 SMS RESULTS:")
    sms_delivered = len([r for r in sms_results if r["status"] == "delivered"])
    sms_failed = len([r for r in sms_results if r["status"] == "failed"])
    print(f"   • Delivered: {sms_delivered}")
    print(f"   • Failed: {sms_failed}")
    print(f"   • Success Rate: {(sms_delivered/len(sms_results)*100):.1f}%")
    
    print(f"\n📞 VOICE CALL RESULTS:")
    calls_answered = len([r for r in call_results if r["status"] == "completed" and r["duration"] and r["duration"] > 0])
    calls_failed = len([r for r in call_results if r["status"] in ["failed", "busy"]])
    print(f"   • Answered: {calls_answered}")
    print(f"   • Failed/Busy: {calls_failed}")
    print(f"   • Total Calls: {len(call_results)}")
    
    avg_duration = sum([r["duration"] for r in call_results if r["duration"]]) / max(len(call_results), 1)
    print(f"   • Avg Duration: {avg_duration:.1f}s")
    
    print(f"\n🎯 EXPECTED OUTCOMES:")
    estimated_bookings = calls_answered * 0.3  # 30% conversion rate
    estimated_revenue = estimated_bookings * 85  # Average service price
    print(f"   • Estimated Bookings: {estimated_bookings:.1f}")
    print(f"   • Estimated Revenue: ${estimated_revenue:.0f}")
    
    print(f"\n✨ NEXT STEPS:")
    print(f"   • Follow up with interested customers in 2 days")
    print(f"   • Monitor booking confirmations")
    print(f"   • Send thank you messages to new bookings")
    
    print("\n" + "=" * 60)
    print("🎉 Demo campaign completed successfully!")
    print("🎭 All interactions were simulated using fake providers")
    print("=" * 60)


def main():
    """Main demo function."""
    print_header()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Get VIP customers
        vip_customers = get_vip_customers(db)
        
        if not vip_customers:
            print("❌ No VIP customers found. Please run 'make seed' first.")
            return
        
        # Step 2: Get active promotions
        active_promotions = get_active_promotions(db)
        
        if not active_promotions:
            print("❌ No active promotions found. Please run 'make seed' first.")
            return
        
        # Use the first active promotion for demo
        promotion = active_promotions[0]
        
        # Step 3: Send SMS campaign
        sms_results = send_sms_campaign(vip_customers, promotion)
        
        # Step 4: Make voice calls
        call_results = make_voice_calls(vip_customers, promotion)
        
        # Step 5: Log results
        log_campaign_results(db, vip_customers, promotion, sms_results, call_results)
        
        # Step 6: Display summary
        display_campaign_summary(vip_customers, promotion, sms_results, call_results)
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
