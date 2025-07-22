"""
API Routes for TwistyVoice

This module defines all API endpoints for the TwistyVoice system.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from models.database import get_db, Customer, Conversation, Booking, Promotion
from core.voice_agent import VoiceAgent
from core.conversation_tracker import ConversationTracker
from core.booking_handler import BookingHandler
from core.promotion_engine import PromotionEngine
from core.report_generator import ReportGenerator
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create main API router
api_router = APIRouter()

# Create sub-routers for different endpoints
webhooks_router = APIRouter(prefix="/webhooks", tags=["webhooks"])
twiml_router = APIRouter(prefix="/twiml", tags=["twiml"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Include sub-routers in main router
api_router.include_router(webhooks_router)
api_router.include_router(twiml_router)
api_router.include_router(admin_router)


# Webhook endpoints for Twilio
@webhooks_router.post("/call_status")
async def handle_call_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Twilio call status webhooks."""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        call_duration = form_data.get("CallDuration")
        recording_url = form_data.get("RecordingUrl")
        
        logger.info(f"Call status update: {call_sid} -> {call_status}")
        
        # Find conversation by call SID
        conversation_tracker = ConversationTracker(db)
        conversation = conversation_tracker.get_conversation_by_call_sid(call_sid)
        
        if conversation:
            conversation_tracker.update_call_status(
                conversation.id,
                call_status,
                int(call_duration) if call_duration else None,
                recording_url
            )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling call status webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@webhooks_router.post("/gather_response")
async def handle_gather_response(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Twilio gather (DTMF) responses."""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        digits = form_data.get("Digits")
        
        logger.info(f"Gather response: {call_sid} -> {digits}")
        
        # Find conversation and log response
        conversation_tracker = ConversationTracker(db)
        conversation = conversation_tracker.get_conversation_by_call_sid(call_sid)
        
        if conversation:
            # Map digits to responses
            response_map = {
                "1": "booked",
                "2": "interested", 
                "3": "callback",
                "9": "remove_from_list"
            }
            
            response = response_map.get(digits, "unknown")
            conversation_tracker.log_customer_response(conversation.id, response)
            
            # If customer wants to book, handle booking logic
            if digits == "1":
                await _handle_booking_request(conversation, db)
        
        # Generate TwiML response
        voice_agent = VoiceAgent()
        twiml_response = voice_agent.generate_response_twiml(digits)
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling gather response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@webhooks_router.post("/sms_status")
async def handle_sms_status(request: Request):
    """Handle Twilio SMS status webhooks."""
    try:
        form_data = await request.form()
        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")
        
        logger.info(f"SMS status update: {message_sid} -> {message_status}")
        
        # TODO: Log SMS status in database if needed
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling SMS status webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@webhooks_router.post("/incoming_sms")
async def handle_incoming_sms(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle incoming SMS messages."""
    try:
        form_data = await request.form()
        from_number = form_data.get("From")
        body = form_data.get("Body")
        
        logger.info(f"Incoming SMS from {from_number}: {body}")
        
        # Find customer by phone number
        customer = db.query(Customer).filter(
            Customer.phone_number == from_number
        ).first()
        
        voice_agent = VoiceAgent()
        response_message = await voice_agent.handle_incoming_sms(from_number, body)
        
        # Send response
        if customer:
            await voice_agent.send_sms(customer, response_message)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling incoming SMS: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# TwiML generation endpoints
@twiml_router.get("/promotional_call")
async def generate_promotional_twiml(
    customer_id: int,
    promotion_id: int,
    db: Session = Depends(get_db)
):
    """Generate TwiML for promotional calls."""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        
        if not customer or not promotion:
            raise HTTPException(status_code=404, detail="Customer or promotion not found")
        
        voice_agent = VoiceAgent()
        twiml_content = voice_agent.generate_promotional_twiml(customer, promotion)
        
        return PlainTextResponse(twiml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error generating promotional TwiML: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Admin endpoints
@admin_router.get("/customers")
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of customers."""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers


@admin_router.get("/customers/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get specific customer details."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@admin_router.get("/customers/{customer_id}/conversations")
async def get_customer_conversations(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation history for a customer."""
    conversation_tracker = ConversationTracker(db)
    conversations = conversation_tracker.get_conversation_history(customer_id)
    return conversations


@admin_router.get("/promotions")
async def get_promotions(db: Session = Depends(get_db)):
    """Get list of promotions."""
    promotions = db.query(Promotion).filter(Promotion.is_active == True).all()
    return promotions


@admin_router.get("/analytics/daily")
async def get_daily_analytics(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get daily analytics."""
    try:
        report_date = datetime.fromisoformat(date) if date else None
        report_generator = ReportGenerator(db)
        report_data = await report_generator.generate_daily_report(report_date)
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating daily analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.get("/analytics/weekly")
async def get_weekly_analytics(
    week_start: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get weekly analytics."""
    try:
        start_date = datetime.fromisoformat(week_start) if week_start else None
        report_generator = ReportGenerator(db)
        report_data = await report_generator.generate_weekly_report(start_date)
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating weekly analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.post("/campaigns/start")
async def start_promotional_campaign(
    promotion_id: int,
    customer_ids: List[int],
    db: Session = Depends(get_db)
):
    """Start a promotional campaign for specific customers."""
    try:
        # Validate promotion exists
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise HTTPException(status_code=404, detail="Promotion not found")
        
        # Validate customers exist and are eligible
        customers = db.query(Customer).filter(
            Customer.id.in_(customer_ids),
            Customer.opt_out_calls == False
        ).all()
        
        if not customers:
            raise HTTPException(status_code=400, detail="No eligible customers found")
        
        # TODO: Implement campaign execution logic
        # This would integrate with the scheduler to start the campaign
        
        return {
            "status": "success",
            "message": f"Campaign started for {len(customers)} customers",
            "campaign_id": f"manual_{datetime.utcnow().timestamp()}"
        }
        
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.get("/bookings")
async def get_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of bookings."""
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings


@admin_router.post("/test/call")
async def test_call(
    customer_id: int,
    promotion_id: int,
    db: Session = Depends(get_db)
):
    """Test call functionality (development only)."""
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Test endpoints only available in debug mode")
    
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        
        if not customer or not promotion:
            raise HTTPException(status_code=404, detail="Customer or promotion not found")
        
        voice_agent = VoiceAgent()
        conversation_tracker = ConversationTracker(db)
        
        # Log test call
        conversation = conversation_tracker.log_call_initiated(
            customer_id=customer.id,
            promotion_id=promotion.id,
            call_type="test"
        )
        
        # Make test call
        call_sid = await voice_agent.make_promotional_call(
            customer=customer,
            promotion=promotion,
            callback_url=settings.TWILIO_WEBHOOK_URL or "http://localhost:8000/api/v1"
        )
        
        return {
            "status": "success",
            "call_sid": call_sid,
            "conversation_id": conversation.id
        }
        
    except Exception as e:
        logger.error(f"Error making test call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _handle_booking_request(conversation: Conversation, db: Session):
    """Handle booking request from customer response."""
    try:
        customer = db.query(Customer).filter(Customer.id == conversation.customer_id).first()
        if not customer:
            return
        
        booking_handler = BookingHandler(db)
        
        # Get next available slots (simplified - in real implementation would be more sophisticated)
        available_slots = await booking_handler.get_next_available_slots(
            service_duration=60,  # Default 1 hour
            count=1
        )
        
        if available_slots:
            # Book the first available slot (simplified)
            slot = available_slots[0]
            booking = await booking_handler.book_appointment(
                customer=customer,
                service_id="default_service",  # Would be determined from promotion/customer preference
                start_time=slot.start_time,
                duration_minutes=slot.duration_minutes,
                conversation_id=conversation.id
            )
            
            if booking:
                logger.info(f"Successfully booked appointment for customer {customer.id}")
        
        await booking_handler.close()
        
    except Exception as e:
        logger.error(f"Error handling booking request: {e}")
