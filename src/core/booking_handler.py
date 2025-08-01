"""
Booking Handler for TwistyVoice

This module manages appointment booking logic:
- Availability checking
- Appointment creation via Square API
- Booking confirmation and notifications
- Conflict resolution
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from core.csv_data_connector import CSVDataConnector
from core.voice_agent import VoiceAgent
from models.database import Customer, Booking, Conversation
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TimeSlot:
    """Represents an available time slot."""
    
    def __init__(self, start_time: datetime, duration_minutes: int, stylist_id: Optional[str] = None):
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.end_time = start_time + timedelta(minutes=duration_minutes)
        self.stylist_id = stylist_id
    
    def __str__(self):
        return f"{self.start_time.strftime('%Y-%m-%d %H:%M')} ({self.duration_minutes}min)"


class BookingHandler:
    """
    Handles appointment booking operations.
    
    This class manages the entire booking process from availability
    checking to confirmation and follow-up communications.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.data_connector = CSVDataConnector()
        self.voice_agent = VoiceAgent()
    
    async def get_available_slots(
        self,
        service_duration: int,
        start_date: datetime,
        end_date: datetime,
        stylist_id: Optional[str] = None
    ) -> List[TimeSlot]:
        """
        Get available appointment slots for a given period.
        
        Args:
            service_duration: Duration of service in minutes
            start_date: Start of search period
            end_date: End of search period
            stylist_id: Optional specific stylist ID
            
        Returns:
            List of available TimeSlot objects
        """
        try:
            # Get existing bookings from Square
            existing_bookings = await self.data_connector.get_bookings(
                start_at=start_date,
                end_at=end_date
            )
            
            # Generate potential time slots
            potential_slots = self._generate_potential_slots(
                start_date, end_date, service_duration
            )
            
            # Filter out conflicting slots
            available_slots = []
            for slot in potential_slots:
                if not self._has_conflict(slot, existing_bookings, stylist_id):
                    available_slots.append(slot)
            
            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    def _generate_potential_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int
    ) -> List[TimeSlot]:
        """
        Generate all potential appointment slots within business hours.
        
        Args:
            start_date: Start of period
            end_date: End of period
            duration_minutes: Service duration
            
        Returns:
            List of potential TimeSlot objects
        """
        slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        # Parse business hours
        start_hour, start_minute = map(int, settings.BUSINESS_HOURS_START.split(':'))
        end_hour, end_minute = map(int, settings.BUSINESS_HOURS_END.split(':'))
        
        while current_date <= end_date_only:
            # Skip weekends (assuming salon is closed)
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Generate slots for this day
            day_start = datetime.combine(current_date, datetime.min.time().replace(
                hour=start_hour, minute=start_minute
            ))
            day_end = datetime.combine(current_date, datetime.min.time().replace(
                hour=end_hour, minute=end_minute
            ))
            
            current_time = day_start
            while current_time + timedelta(minutes=duration_minutes) <= day_end:
                slots.append(TimeSlot(current_time, duration_minutes))
                current_time += timedelta(minutes=30)  # 30-minute intervals
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _has_conflict(
        self,
        slot: TimeSlot,
        existing_bookings: List,
        stylist_id: Optional[str] = None
    ) -> bool:
        """
        Check if a time slot conflicts with existing bookings.
        
        Args:
            slot: TimeSlot to check
            existing_bookings: List of existing Square bookings
            stylist_id: Optional stylist ID to check conflicts for
            
        Returns:
            True if there's a conflict, False otherwise
        """
        for booking in existing_bookings:
            # Parse booking time
            for segment in booking.appointment_segments:
                booking_start = datetime.fromisoformat(
                    segment['start_at'].replace('Z', '+00:00')
                ).replace(tzinfo=None)
                booking_duration = segment.get('duration_minutes', 60)
                booking_end = booking_start + timedelta(minutes=booking_duration)
                
                # Check for time overlap
                if (slot.start_time < booking_end and slot.end_time > booking_start):
                    # If checking specific stylist, only conflict if same stylist
                    if stylist_id:
                        booking_stylist = segment.get('team_member_id')
                        if booking_stylist == stylist_id:
                            return True
                    else:
                        # General conflict (assuming limited capacity)
                        return True
        
        return False
    
    async def book_appointment(
        self,
        customer: Customer,
        service_id: str,
        start_time: datetime,
        duration_minutes: int,
        stylist_id: Optional[str] = None,
        conversation_id: Optional[int] = None
    ) -> Optional[Booking]:
        """
        Book an appointment for a customer.
        
        Args:
            customer: Customer to book for
            service_id: Square service ID
            start_time: Appointment start time
            duration_minutes: Service duration
            stylist_id: Optional stylist ID
            conversation_id: Optional conversation that led to booking
            
        Returns:
            Booking object if successful, None otherwise
        """
        try:
            # Create booking in Square
            booking_id = await self.data_connector.create_booking(
                customer_id=customer.square_customer_id,
                service_id=service_id,
                start_time=start_time,
                duration_minutes=duration_minutes,
                team_member_id=stylist_id
            )
            
            if not booking_id:
                logger.error("Failed to create booking in Square")
                return None
            
            # Get service details
            services = await self.data_connector.get_catalog_services()
            service_name = "Hair Service"  # Default
            service_price = 0.0
            
            for service in services:
                if service.id == service_id:
                    service_name = service.name
                    if service.price_money:
                        service_price = service.price_money.get('amount', 0) / 100
                    break
            
            # Create local booking record
            booking = Booking(
                customer_id=customer.id,
                conversation_id=conversation_id,
                external_booking_id=booking_id,
                appointment_datetime=start_time,
                service_name=service_name,
                stylist_name="",  # TODO: Get stylist name from CSV
                duration_minutes=duration_minutes,
                price=service_price,
                status="confirmed",
                created_via="voice_call" if conversation_id else "manual"
            )
            
            self.db.add(booking)
            self.db.commit()
            self.db.refresh(booking)
            
            # Send confirmation SMS
            await self._send_booking_confirmation(customer, booking)
            
            # Update customer stats
            customer.total_visits += 1
            customer.total_spent += service_price
            customer.last_visit_date = start_time
            self.db.commit()
            
            logger.info(f"Successfully booked appointment {booking.id} for customer {customer.id}")
            return booking
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            self.db.rollback()
            return None
    
    async def _send_booking_confirmation(self, customer: Customer, booking: Booking):
        """
        Send booking confirmation via SMS.
        
        Args:
            customer: Customer who booked
            booking: Booking details
        """
        try:
            confirmation_message = self._generate_confirmation_message(customer, booking)
            await self.voice_agent.send_sms(customer, confirmation_message)
            
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {e}")
    
    def _generate_confirmation_message(self, customer: Customer, booking: Booking) -> str:
        """
        Generate booking confirmation message.
        
        Args:
            customer: Customer who booked
            booking: Booking details
            
        Returns:
            Confirmation message text
        """
        customer_name = customer.first_name or "valued customer"
        apt_time = booking.appointment_datetime.strftime("%A, %B %d at %I:%M %p")
        
        message = (
            f"Hi {customer_name}! Your {booking.service_name} appointment at "
            f"{settings.SALON_NAME} is confirmed for {apt_time}. "
            f"Address: {settings.SALON_ADDRESS}. "
            f"Questions? Call {settings.SALON_PHONE}."
        )
        
        return message
    
    async def get_next_available_slots(
        self,
        service_duration: int,
        count: int = 5,
        days_ahead: int = 14
    ) -> List[TimeSlot]:
        """
        Get the next available appointment slots.
        
        Args:
            service_duration: Duration of service in minutes
            count: Number of slots to return
            days_ahead: How many days ahead to search
            
        Returns:
            List of next available TimeSlot objects
        """
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        all_slots = await self.get_available_slots(
            service_duration, start_date, end_date
        )
        
        # Return the first 'count' slots
        return all_slots[:count]
    
    async def suggest_alternative_times(
        self,
        preferred_time: datetime,
        service_duration: int,
        window_hours: int = 4
    ) -> List[TimeSlot]:
        """
        Suggest alternative appointment times near a preferred time.
        
        Args:
            preferred_time: Customer's preferred appointment time
            service_duration: Duration of service in minutes
            window_hours: Hours before/after preferred time to search
            
        Returns:
            List of alternative TimeSlot objects
        """
        start_search = preferred_time - timedelta(hours=window_hours)
        end_search = preferred_time + timedelta(hours=window_hours)
        
        available_slots = await self.get_available_slots(
            service_duration, start_search, end_search
        )
        
        # Sort by proximity to preferred time
        available_slots.sort(
            key=lambda slot: abs((slot.start_time - preferred_time).total_seconds())
        )
        
        return available_slots[:5]  # Return top 5 alternatives
    
    async def cancel_booking(self, booking_id: int, reason: str = "customer_request") -> bool:
        """
        Cancel an existing booking.
        
        Args:
            booking_id: ID of booking to cancel
            reason: Reason for cancellation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                logger.error(f"Booking {booking_id} not found")
                return False
            
            # TODO: Cancel in Square API
            # For now, just update local status
            booking.status = "cancelled"
            self.db.commit()
            
            # Send cancellation notification
            customer = self.db.query(Customer).filter(Customer.id == booking.customer_id).first()
            if customer:
                await self._send_cancellation_notification(customer, booking)
            
            logger.info(f"Cancelled booking {booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling booking {booking_id}: {e}")
            return False
    
    async def _send_cancellation_notification(self, customer: Customer, booking: Booking):
        """
        Send cancellation notification via SMS.
        
        Args:
            customer: Customer whose booking was cancelled
            booking: Cancelled booking details
        """
        try:
            customer_name = customer.first_name or "valued customer"
            apt_time = booking.appointment_datetime.strftime("%A, %B %d at %I:%M %p")
            
            message = (
                f"Hi {customer_name}, your {booking.service_name} appointment "
                f"on {apt_time} has been cancelled. "
                f"To reschedule, please call {settings.SALON_PHONE}."
            )
            
            await self.voice_agent.send_sms(customer, message)
            
        except Exception as e:
            logger.error(f"Error sending cancellation notification: {e}")
    
    async def send_appointment_reminders(self, hours_ahead: int = 24):
        """
        Send appointment reminders for upcoming bookings.
        
        Args:
            hours_ahead: How many hours ahead to send reminders
        """
        try:
            reminder_time = datetime.utcnow() + timedelta(hours=hours_ahead)
            start_window = reminder_time - timedelta(hours=1)
            end_window = reminder_time + timedelta(hours=1)
            
            upcoming_bookings = self.db.query(Booking).filter(
                Booking.appointment_datetime.between(start_window, end_window),
                Booking.status == "confirmed"
            ).all()
            
            for booking in upcoming_bookings:
                customer = self.db.query(Customer).filter(
                    Customer.id == booking.customer_id
                ).first()
                
                if customer and not customer.opt_out_sms:
                    reminder_message = self.voice_agent.generate_reminder_sms(
                        customer,
                        booking.appointment_datetime,
                        booking.service_name
                    )
                    await self.voice_agent.send_sms(customer, reminder_message)
            
            logger.info(f"Sent {len(upcoming_bookings)} appointment reminders")
            
        except Exception as e:
            logger.error(f"Error sending appointment reminders: {e}")
    
    async def close(self):
        """Close connections."""
        await self.data_connector.close()
