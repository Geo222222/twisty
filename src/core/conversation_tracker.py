"""
Conversation Tracker for TwistyVoice

This module tracks and logs all customer interactions:
- Call outcomes and responses
- Customer preferences and feedback
- Follow-up scheduling
- Interaction analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Customer, Conversation, Promotion, Booking
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ConversationTracker:
    """
    Tracks and manages customer conversation data.
    
    This class handles logging of all customer interactions,
    analyzing conversation outcomes, and scheduling follow-ups.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_call_initiated(
        self,
        customer_id: int,
        promotion_id: Optional[int] = None,
        call_type: str = "promotional",
        twilio_call_sid: Optional[str] = None
    ) -> Conversation:
        """
        Log the initiation of a call.
        
        Args:
            customer_id: ID of customer being called
            promotion_id: Optional promotion being discussed
            call_type: Type of call (promotional, reminder, follow_up)
            twilio_call_sid: Twilio call SID for tracking
            
        Returns:
            Created Conversation object
        """
        conversation = Conversation(
            customer_id=customer_id,
            promotion_id=promotion_id,
            call_type=call_type,
            call_status="initiated",
            twilio_call_sid=twilio_call_sid
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Logged call initiation for customer {customer_id}")
        return conversation
    
    def update_call_status(
        self,
        conversation_id: int,
        status: str,
        duration: Optional[int] = None,
        recording_url: Optional[str] = None
    ):
        """
        Update call status and details.
        
        Args:
            conversation_id: ID of conversation to update
            status: New call status (ringing, answered, completed, failed, etc.)
            duration: Call duration in seconds
            recording_url: URL of call recording
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.call_status = status
            if duration is not None:
                conversation.call_duration = duration
            if recording_url:
                conversation.recording_url = recording_url
            conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Updated conversation {conversation_id} status to {status}")
    
    def log_customer_response(
        self,
        conversation_id: int,
        response: str,
        notes: Optional[str] = None,
        follow_up_required: bool = False,
        follow_up_date: Optional[datetime] = None
    ):
        """
        Log customer response to the call.
        
        Args:
            conversation_id: ID of conversation
            response: Customer response (interested, not_interested, booked, callback, etc.)
            notes: Additional notes about the interaction
            follow_up_required: Whether follow-up is needed
            follow_up_date: When to follow up
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.customer_response = response
            conversation.notes = notes
            conversation.follow_up_required = follow_up_required
            conversation.follow_up_date = follow_up_date
            conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Update customer preferences based on response
            self._update_customer_preferences(conversation.customer_id, response, notes)
            
            logger.info(f"Logged customer response '{response}' for conversation {conversation_id}")
    
    def _update_customer_preferences(
        self,
        customer_id: int,
        response: str,
        notes: Optional[str] = None
    ):
        """
        Update customer preferences based on their response.
        
        Args:
            customer_id: ID of customer
            response: Customer response
            notes: Additional notes
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return
        
        # Update opt-out preferences based on response
        if response in ["not_interested", "remove_from_list"]:
            customer.opt_out_calls = True
            logger.info(f"Customer {customer_id} opted out of calls")
        
        # Analyze notes for preferences (simple keyword matching)
        if notes:
            notes_lower = notes.lower()
            
            # Extract preferred contact times
            if "morning" in notes_lower:
                customer.preferred_contact_time = "morning"
            elif "afternoon" in notes_lower:
                customer.preferred_contact_time = "afternoon"
            elif "evening" in notes_lower:
                customer.preferred_contact_time = "evening"
            
            # Extract service preferences
            services = []
            if "braids" in notes_lower or "braid" in notes_lower:
                services.append("braids")
            if "color" in notes_lower or "coloring" in notes_lower:
                services.append("color")
            if "cut" in notes_lower or "trim" in notes_lower:
                services.append("cut")
            if "style" in notes_lower or "styling" in notes_lower:
                services.append("styling")
            
            if services:
                import json
                existing_services = []
                if customer.preferred_services:
                    try:
                        existing_services = json.loads(customer.preferred_services)
                    except:
                        pass
                
                # Merge with existing preferences
                all_services = list(set(existing_services + services))
                customer.preferred_services = json.dumps(all_services)
        
        self.db.commit()
    
    def get_conversation_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Conversation]:
        """
        Get conversation history for a customer.
        
        Args:
            customer_id: ID of customer
            limit: Maximum number of conversations to return
            
        Returns:
            List of Conversation objects
        """
        conversations = self.db.query(Conversation).filter(
            Conversation.customer_id == customer_id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
        
        return conversations
    
    def get_follow_up_queue(self, days_ahead: int = 7) -> List[Conversation]:
        """
        Get conversations that require follow-up.
        
        Args:
            days_ahead: How many days ahead to look for follow-ups
            
        Returns:
            List of Conversation objects requiring follow-up
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        follow_ups = self.db.query(Conversation).filter(
            Conversation.follow_up_required == True,
            Conversation.follow_up_date <= cutoff_date
        ).order_by(Conversation.follow_up_date).all()
        
        return follow_ups
    
    def mark_follow_up_completed(self, conversation_id: int):
        """
        Mark a follow-up as completed.
        
        Args:
            conversation_id: ID of conversation
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.follow_up_required = False
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Marked follow-up completed for conversation {conversation_id}")
    
    def get_call_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get call analytics for a date range.
        
        Args:
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            Dictionary with analytics data
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        conversations = self.db.query(Conversation).filter(
            Conversation.created_at.between(start_date, end_date)
        ).all()
        
        total_calls = len(conversations)
        if total_calls == 0:
            return {
                "total_calls": 0,
                "answer_rate": 0,
                "interest_rate": 0,
                "booking_rate": 0,
                "opt_out_rate": 0
            }
        
        # Calculate metrics
        answered_calls = len([c for c in conversations if c.call_status == "answered"])
        interested_responses = len([c for c in conversations if c.customer_response == "interested"])
        booked_responses = len([c for c in conversations if c.customer_response == "booked"])
        opt_out_responses = len([c for c in conversations if c.customer_response in ["not_interested", "remove_from_list"]])
        
        analytics = {
            "total_calls": total_calls,
            "answered_calls": answered_calls,
            "interested_responses": interested_responses,
            "booked_responses": booked_responses,
            "opt_out_responses": opt_out_responses,
            "answer_rate": answered_calls / total_calls if total_calls > 0 else 0,
            "interest_rate": interested_responses / answered_calls if answered_calls > 0 else 0,
            "booking_rate": booked_responses / answered_calls if answered_calls > 0 else 0,
            "opt_out_rate": opt_out_responses / total_calls if total_calls > 0 else 0,
            "avg_call_duration": sum(c.call_duration or 0 for c in conversations) / answered_calls if answered_calls > 0 else 0
        }
        
        return analytics
    
    def get_customer_engagement_score(self, customer_id: int) -> float:
        """
        Calculate engagement score for a customer based on interaction history.
        
        Args:
            customer_id: ID of customer
            
        Returns:
            Engagement score (0-100)
        """
        conversations = self.get_conversation_history(customer_id, limit=20)
        
        if not conversations:
            return 0.0
        
        score = 50.0  # Base score
        
        for conversation in conversations:
            # Positive responses increase score
            if conversation.customer_response == "booked":
                score += 15
            elif conversation.customer_response == "interested":
                score += 10
            elif conversation.customer_response == "callback":
                score += 5
            
            # Negative responses decrease score
            elif conversation.customer_response == "not_interested":
                score -= 10
            elif conversation.customer_response == "remove_from_list":
                score -= 20
            
            # Call status affects score
            if conversation.call_status == "answered":
                score += 2
            elif conversation.call_status == "voicemail":
                score -= 1
            elif conversation.call_status == "busy":
                score -= 0.5
        
        # Recency bonus/penalty
        if conversations:
            days_since_last = (datetime.utcnow() - conversations[0].created_at).days
            if days_since_last < 30:
                score += 5
            elif days_since_last > 90:
                score -= 10
        
        # Clamp score between 0 and 100
        return max(0.0, min(100.0, score))
    
    def get_best_contact_time(self, customer_id: int) -> Optional[str]:
        """
        Determine the best time to contact a customer based on history.
        
        Args:
            customer_id: ID of customer
            
        Returns:
            Best contact time ("morning", "afternoon", "evening") or None
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        
        # Check explicit preference first
        if customer and customer.preferred_contact_time:
            return customer.preferred_contact_time
        
        # Analyze successful call times
        conversations = self.db.query(Conversation).filter(
            Conversation.customer_id == customer_id,
            Conversation.call_status == "answered"
        ).all()
        
        if not conversations:
            return None
        
        # Count successful calls by time of day
        time_counts = {"morning": 0, "afternoon": 0, "evening": 0}
        
        for conversation in conversations:
            hour = conversation.created_at.hour
            if 6 <= hour < 12:
                time_counts["morning"] += 1
            elif 12 <= hour < 18:
                time_counts["afternoon"] += 1
            elif 18 <= hour < 22:
                time_counts["evening"] += 1
        
        # Return time with most successful calls
        if any(time_counts.values()):
            return max(time_counts, key=time_counts.get)
        
        return None
    
    def schedule_follow_up(
        self,
        conversation_id: int,
        follow_up_date: datetime,
        notes: Optional[str] = None
    ):
        """
        Schedule a follow-up for a conversation.
        
        Args:
            conversation_id: ID of conversation
            follow_up_date: When to follow up
            notes: Additional notes for follow-up
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.follow_up_required = True
            conversation.follow_up_date = follow_up_date
            if notes:
                existing_notes = conversation.notes or ""
                conversation.notes = f"{existing_notes}\nFollow-up: {notes}".strip()
            conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Scheduled follow-up for conversation {conversation_id} on {follow_up_date}")
    
    def get_conversation_by_call_sid(self, call_sid: str) -> Optional[Conversation]:
        """
        Get conversation by Twilio call SID.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Conversation object or None
        """
        return self.db.query(Conversation).filter(
            Conversation.twilio_call_sid == call_sid
        ).first()
