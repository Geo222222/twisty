"""
Voice Agent for TwistyVoice

This module handles voice calls and SMS messaging using Twilio:
- Text-to-speech generation
- Interactive voice response (IVR)
- SMS messaging
- Call recording and transcription
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from twilio.rest import Client
from twilio.twiml import VoiceResponse
import httpx

from config.settings import get_settings
from models.database import Customer, Promotion

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceAgent:
    """
    Voice and SMS agent using Twilio for customer communications.
    
    This class handles:
    - Outbound promotional calls
    - Interactive voice responses
    - SMS messaging
    - Call recording and logging
    """
    
    def __init__(self):
        self.twilio_client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    async def make_promotional_call(
        self,
        customer: Customer,
        promotion: Promotion,
        callback_url: str
    ) -> Optional[str]:
        """
        Make a promotional call to a customer.
        
        Args:
            customer: Customer to call
            promotion: Promotion to discuss
            callback_url: URL for Twilio webhooks
            
        Returns:
            Call SID if successful, None otherwise
        """
        if settings.MOCK_CALLS:
            logger.info(f"MOCK CALL: Would call {customer.phone_number} about {promotion.name}")
            return "mock_call_sid_123"
        
        try:
            # Generate TwiML for the call
            twiml_url = f"{callback_url}/twiml/promotional_call"
            
            # Make the call
            call = self.twilio_client.calls.create(
                to=customer.phone_number,
                from_=self.from_number,
                url=f"{twiml_url}?customer_id={customer.id}&promotion_id={promotion.id}",
                status_callback=f"{callback_url}/webhooks/call_status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                record=True,
                timeout=30,
                machine_detection="Enable"
            )
            
            logger.info(f"Initiated call {call.sid} to {customer.phone_number}")
            return call.sid
            
        except Exception as e:
            logger.error(f"Error making call to {customer.phone_number}: {e}")
            return None
    
    def generate_promotional_twiml(
        self,
        customer: Customer,
        promotion: Promotion
    ) -> str:
        """
        Generate TwiML for a promotional call.
        
        Args:
            customer: Customer being called
            promotion: Promotion being offered
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        # Personalized greeting
        greeting = self._generate_greeting_text(customer, promotion)
        response.say(greeting, voice="alice", language="en-US")
        
        # Pause for customer to process
        response.pause(length=2)
        
        # Present options
        gather = response.gather(
            num_digits=1,
            timeout=10,
            action="/api/v1/webhooks/gather_response",
            method="POST"
        )
        
        options_text = (
            "To book an appointment now, press 1. "
            "To hear more details about this offer, press 2. "
            "To speak with someone, press 3. "
            "To be removed from our call list, press 9."
        )
        gather.say(options_text, voice="alice", language="en-US")
        
        # Default action if no input
        response.say(
            "I didn't receive a response. I'll send you a text message with the details. "
            "Have a wonderful day!",
            voice="alice",
            language="en-US"
        )
        response.hangup()
        
        return str(response)
    
    def _generate_greeting_text(self, customer: Customer, promotion: Promotion) -> str:
        """
        Generate personalized greeting text for a customer.
        
        Args:
            customer: Customer being called
            promotion: Promotion being offered
            
        Returns:
            Greeting text string
        """
        customer_name = customer.first_name or "valued customer"
        salon_name = settings.SALON_NAME
        
        # Base greeting
        greeting = f"Hi {customer_name}, this is TwistyVoice calling from {salon_name}. "
        
        # Add context based on customer history
        if customer.last_visit_date:
            days_since_visit = (datetime.utcnow() - customer.last_visit_date).days
            if days_since_visit > 60:
                greeting += "We miss seeing you! "
            elif days_since_visit > 30:
                greeting += "It's been a while since your last visit. "
        else:
            greeting += "We'd love to welcome you to our salon. "
        
        # Add promotion details
        if promotion.discount_percentage:
            greeting += f"I'm calling to let you know about our special {promotion.discount_percentage}% off promotion"
        elif promotion.discount_amount:
            greeting += f"I'm calling to let you know about our special ${promotion.discount_amount} off promotion"
        else:
            greeting += f"I'm calling to let you know about our special promotion"
        
        if promotion.name:
            greeting += f" - {promotion.name}. "
        else:
            greeting += ". "
        
        # Add urgency if applicable
        if promotion.end_date:
            days_until_end = (promotion.end_date - datetime.utcnow()).days
            if days_until_end <= 7:
                greeting += f"This offer ends in {days_until_end} days, so don't miss out! "
        
        return greeting
    
    def generate_response_twiml(self, digit_pressed: str) -> str:
        """
        Generate TwiML response based on customer input.
        
        Args:
            digit_pressed: Digit pressed by customer
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        if digit_pressed == "1":
            # Book appointment
            response.say(
                "Great! I'll connect you with our booking system. "
                "Please hold while I transfer you.",
                voice="alice",
                language="en-US"
            )
            # In a real implementation, this would connect to booking system
            response.dial(settings.SALON_PHONE)
            
        elif digit_pressed == "2":
            # More details
            response.say(
                "I'll send you a text message with all the details about this promotion. "
                "You can also visit our website or call us directly to book. "
                "Thank you for your time!",
                voice="alice",
                language="en-US"
            )
            response.hangup()
            
        elif digit_pressed == "3":
            # Speak with someone
            response.say(
                "I'll connect you with one of our team members. Please hold.",
                voice="alice",
                language="en-US"
            )
            response.dial(settings.SALON_PHONE)
            
        elif digit_pressed == "9":
            # Opt out
            response.say(
                "I understand. You've been removed from our call list. "
                "You can still visit us anytime or call us directly. "
                "Have a great day!",
                voice="alice",
                language="en-US"
            )
            response.hangup()
            
        else:
            # Invalid input
            response.say(
                "I didn't understand that selection. "
                "I'll send you a text with the promotion details. "
                "Feel free to call us directly if you're interested. "
                "Thank you!",
                voice="alice",
                language="en-US"
            )
            response.hangup()
        
        return str(response)
    
    async def send_sms(
        self,
        customer: Customer,
        message: str,
        promotion: Optional[Promotion] = None
    ) -> Optional[str]:
        """
        Send an SMS message to a customer.
        
        Args:
            customer: Customer to send SMS to
            message: Message content
            promotion: Optional promotion context
            
        Returns:
            Message SID if successful, None otherwise
        """
        if settings.MOCK_SMS:
            logger.info(f"MOCK SMS: Would send to {customer.phone_number}: {message}")
            return "mock_sms_sid_123"
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.from_number,
                to=customer.phone_number,
                status_callback="/api/v1/webhooks/sms_status"
            )
            
            logger.info(f"Sent SMS {message.sid} to {customer.phone_number}")
            return message.sid
            
        except Exception as e:
            logger.error(f"Error sending SMS to {customer.phone_number}: {e}")
            return None
    
    def generate_promotional_sms(
        self,
        customer: Customer,
        promotion: Promotion
    ) -> str:
        """
        Generate promotional SMS content.
        
        Args:
            customer: Customer receiving SMS
            promotion: Promotion being offered
            
        Returns:
            SMS message text
        """
        customer_name = customer.first_name or "valued customer"
        salon_name = settings.SALON_NAME
        
        message = f"Hi {customer_name}! {salon_name} here. "
        
        # Add promotion details
        if promotion.discount_percentage:
            message += f"Special offer: {promotion.discount_percentage}% off "
        elif promotion.discount_amount:
            message += f"Special offer: ${promotion.discount_amount} off "
        
        if promotion.name:
            message += f"{promotion.name}. "
        
        if promotion.description:
            message += f"{promotion.description} "
        
        # Add urgency
        if promotion.end_date:
            days_until_end = (promotion.end_date - datetime.utcnow()).days
            if days_until_end <= 7:
                message += f"Ends in {days_until_end} days! "
        
        # Add call to action
        message += f"Book now: {settings.SALON_PHONE} "
        
        # Add opt-out
        message += "Reply STOP to opt out."
        
        return message
    
    def generate_reminder_sms(
        self,
        customer: Customer,
        appointment_datetime: datetime,
        service_name: str
    ) -> str:
        """
        Generate appointment reminder SMS.
        
        Args:
            customer: Customer with appointment
            appointment_datetime: Appointment date and time
            service_name: Name of booked service
            
        Returns:
            SMS reminder text
        """
        customer_name = customer.first_name or "valued customer"
        salon_name = settings.SALON_NAME
        
        # Format appointment time
        apt_time = appointment_datetime.strftime("%A, %B %d at %I:%M %p")
        
        message = (
            f"Hi {customer_name}! Reminder: You have a {service_name} appointment "
            f"at {salon_name} on {apt_time}. "
            f"Questions? Call {settings.SALON_PHONE}. "
            f"Address: {settings.SALON_ADDRESS}"
        )
        
        return message
    
    async def handle_incoming_sms(self, from_number: str, body: str) -> str:
        """
        Handle incoming SMS messages.
        
        Args:
            from_number: Phone number that sent the message
            body: Message content
            
        Returns:
            Response message
        """
        body_lower = body.lower().strip()
        
        # Handle opt-out keywords
        opt_out_keywords = settings.AUTO_OPT_OUT_KEYWORDS.lower().split(",")
        if any(keyword.strip() in body_lower for keyword in opt_out_keywords):
            # TODO: Update customer opt-out status in database
            return (
                f"You've been removed from {settings.SALON_NAME} text messages. "
                f"You can still call us at {settings.SALON_PHONE} anytime."
            )
        
        # Handle booking requests
        if any(word in body_lower for word in ["book", "appointment", "schedule"]):
            return (
                f"Great! Please call {settings.SALON_PHONE} to book your appointment, "
                f"or visit us at {settings.SALON_ADDRESS}. "
                f"Our hours are {settings.BUSINESS_HOURS_START}-{settings.BUSINESS_HOURS_END}."
            )
        
        # Handle questions
        if any(word in body_lower for word in ["?", "question", "info", "details"]):
            return (
                f"Thanks for your message! For questions about services or promotions, "
                f"please call {settings.SALON_PHONE} and our team will be happy to help!"
            )
        
        # Default response
        return (
            f"Thanks for contacting {settings.SALON_NAME}! "
            f"For immediate assistance, please call {settings.SALON_PHONE}."
        )
