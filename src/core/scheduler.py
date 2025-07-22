"""
Scheduler for TwistyVoice

This module handles all scheduled tasks:
- Promotional call campaigns
- Appointment reminders
- Daily/weekly reports
- Follow-up calls
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from models.database import get_db, Customer, Promotion, CallCampaign, Conversation
from core.square_connector import SquareConnector
from core.promotion_engine import PromotionEngine
from core.voice_agent import VoiceAgent
from core.booking_handler import BookingHandler
from core.conversation_tracker import ConversationTracker
from core.report_generator import ReportGenerator
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TwistyScheduler:
    """
    Main scheduler for TwistyVoice automated tasks.
    
    This class manages all scheduled operations including:
    - Promotional call campaigns
    - Appointment reminders
    - Report generation
    - Follow-up scheduling
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start(self):
        """Start the scheduler and set up all scheduled jobs."""
        if self.is_running:
            return
        
        logger.info("Starting TwistyVoice scheduler")
        
        # Schedule daily reports (8 AM every day)
        self.scheduler.add_job(
            self.send_daily_reports,
            CronTrigger(hour=8, minute=0),
            id="daily_reports",
            name="Send Daily Reports"
        )
        
        # Schedule weekly reports (Monday 9 AM)
        self.scheduler.add_job(
            self.send_weekly_reports,
            CronTrigger(day_of_week=0, hour=9, minute=0),
            id="weekly_reports",
            name="Send Weekly Reports"
        )
        
        # Schedule appointment reminders (every hour during business hours)
        self.scheduler.add_job(
            self.send_appointment_reminders,
            CronTrigger(hour="9-18", minute=0),
            id="appointment_reminders",
            name="Send Appointment Reminders"
        )
        
        # Schedule follow-up calls (every 2 hours during business hours)
        self.scheduler.add_job(
            self.process_follow_ups,
            CronTrigger(hour="9-17/2", minute=30),
            id="follow_up_calls",
            name="Process Follow-up Calls"
        )
        
        # Schedule promotional campaigns (weekdays at 10 AM and 2 PM)
        self.scheduler.add_job(
            self.run_promotional_campaigns,
            CronTrigger(day_of_week="0-4", hour="10,14", minute=0),
            id="promotional_campaigns",
            name="Run Promotional Campaigns"
        )
        
        # Schedule database cleanup (daily at midnight)
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=0, minute=0),
            id="database_cleanup",
            name="Database Cleanup"
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("TwistyVoice scheduler started successfully")
    
    async def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        logger.info("Stopping TwistyVoice scheduler")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("TwistyVoice scheduler stopped")
    
    async def send_daily_reports(self):
        """Send daily reports to management."""
        try:
            logger.info("Generating and sending daily reports")
            
            db = next(get_db())
            report_generator = ReportGenerator(db)
            
            await report_generator.send_daily_report_email()
            
            db.close()
            logger.info("Daily reports sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending daily reports: {e}")
    
    async def send_weekly_reports(self):
        """Send weekly reports to management."""
        try:
            logger.info("Generating and sending weekly reports")
            
            db = next(get_db())
            report_generator = ReportGenerator(db)
            
            await report_generator.send_weekly_report_email()
            
            db.close()
            logger.info("Weekly reports sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending weekly reports: {e}")
    
    async def send_appointment_reminders(self):
        """Send appointment reminders for upcoming bookings."""
        try:
            logger.info("Sending appointment reminders")
            
            db = next(get_db())
            booking_handler = BookingHandler(db)
            
            # Send reminders for appointments 24 hours ahead
            await booking_handler.send_appointment_reminders(hours_ahead=24)
            
            await booking_handler.close()
            db.close()
            logger.info("Appointment reminders sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending appointment reminders: {e}")
    
    async def process_follow_ups(self):
        """Process scheduled follow-up calls."""
        try:
            logger.info("Processing follow-up calls")
            
            db = next(get_db())
            conversation_tracker = ConversationTracker(db)
            
            # Get follow-ups due in the next 2 hours
            follow_ups = conversation_tracker.get_follow_up_queue(days_ahead=0)
            
            for conversation in follow_ups:
                # Check if it's time for this follow-up
                if conversation.follow_up_date <= datetime.utcnow():
                    await self._make_follow_up_call(conversation, db)
            
            db.close()
            logger.info(f"Processed {len(follow_ups)} follow-up calls")
            
        except Exception as e:
            logger.error(f"Error processing follow-ups: {e}")
    
    async def _make_follow_up_call(self, conversation: Conversation, db: Session):
        """Make a follow-up call for a conversation."""
        try:
            customer = db.query(Customer).filter(Customer.id == conversation.customer_id).first()
            if not customer or customer.opt_out_calls:
                return
            
            # Check if it's appropriate time to call
            if not self._is_appropriate_call_time():
                # Reschedule for later
                conversation.follow_up_date = datetime.utcnow() + timedelta(hours=2)
                db.commit()
                return
            
            voice_agent = VoiceAgent()
            conversation_tracker = ConversationTracker(db)
            
            # Create new conversation for follow-up
            new_conversation = conversation_tracker.log_call_initiated(
                customer_id=customer.id,
                promotion_id=conversation.promotion_id,
                call_type="follow_up"
            )
            
            # Make the call (this would integrate with actual call logic)
            call_sid = await voice_agent.make_promotional_call(
                customer=customer,
                promotion=conversation.promotion,
                callback_url=settings.TWILIO_WEBHOOK_URL
            )
            
            if call_sid:
                new_conversation.twilio_call_sid = call_sid
                conversation.follow_up_required = False  # Mark original as completed
                db.commit()
            
            logger.info(f"Made follow-up call for customer {customer.id}")
            
        except Exception as e:
            logger.error(f"Error making follow-up call: {e}")
    
    async def run_promotional_campaigns(self):
        """Run scheduled promotional campaigns."""
        try:
            logger.info("Running promotional campaigns")
            
            db = next(get_db())
            
            # Check if we've reached daily call limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_calls = db.query(Conversation).filter(
                Conversation.created_at >= today_start
            ).count()
            
            if today_calls >= settings.MAX_CALLS_PER_DAY:
                logger.info(f"Daily call limit reached ({today_calls}/{settings.MAX_CALLS_PER_DAY})")
                db.close()
                return
            
            # Get eligible customers for promotional calls
            eligible_customers = await self._get_eligible_customers_for_promotion(db)
            
            if not eligible_customers:
                logger.info("No eligible customers for promotional campaigns")
                db.close()
                return
            
            # Limit calls for this session
            remaining_calls = settings.MAX_CALLS_PER_DAY - today_calls
            session_limit = min(10, remaining_calls)  # Max 10 calls per session
            
            customers_to_call = eligible_customers[:session_limit]
            
            await self._execute_promotional_campaign(customers_to_call, db)
            
            db.close()
            logger.info(f"Promotional campaign completed - called {len(customers_to_call)} customers")
            
        except Exception as e:
            logger.error(f"Error running promotional campaigns: {e}")
    
    async def _get_eligible_customers_for_promotion(self, db: Session) -> List[Customer]:
        """Get customers eligible for promotional calls."""
        # Get customers who haven't been called recently
        cutoff_date = datetime.utcnow() - timedelta(days=14)
        
        eligible_customers = db.query(Customer).filter(
            Customer.opt_out_calls == False,
            ~Customer.conversations.any(Conversation.created_at > cutoff_date)
        ).limit(50).all()  # Limit query size
        
        # Filter by appropriate call time preferences
        filtered_customers = []
        for customer in eligible_customers:
            if self._is_good_time_for_customer(customer):
                filtered_customers.append(customer)
        
        return filtered_customers
    
    def _is_good_time_for_customer(self, customer: Customer) -> bool:
        """Check if current time is good for calling this customer."""
        current_hour = datetime.utcnow().hour
        
        # Respect customer's preferred contact time
        if customer.preferred_contact_time:
            if customer.preferred_contact_time == "morning" and 9 <= current_hour < 12:
                return True
            elif customer.preferred_contact_time == "afternoon" and 12 <= current_hour < 17:
                return True
            elif customer.preferred_contact_time == "evening" and 17 <= current_hour < 20:
                return True
            else:
                return False
        
        # Default business hours
        return 9 <= current_hour < 18
    
    async def _execute_promotional_campaign(self, customers: List[Customer], db: Session):
        """Execute promotional campaign for a list of customers."""
        voice_agent = VoiceAgent()
        promotion_engine = PromotionEngine(db)
        conversation_tracker = ConversationTracker(db)
        
        for customer in customers:
            try:
                # Select best promotion for this customer
                promotion = promotion_engine.select_best_promotion(customer)
                if not promotion:
                    continue
                
                # Log call initiation
                conversation = conversation_tracker.log_call_initiated(
                    customer_id=customer.id,
                    promotion_id=promotion.id,
                    call_type="promotional"
                )
                
                # Make the call
                call_sid = await voice_agent.make_promotional_call(
                    customer=customer,
                    promotion=promotion,
                    callback_url=settings.TWILIO_WEBHOOK_URL
                )
                
                if call_sid:
                    conversation.twilio_call_sid = call_sid
                    db.commit()
                
                # Small delay between calls
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error calling customer {customer.id}: {e}")
                continue
    
    def _is_appropriate_call_time(self) -> bool:
        """Check if current time is appropriate for making calls."""
        current_hour = datetime.utcnow().hour
        
        # Respect do not disturb hours
        if settings.RESPECT_DND_HOURS:
            if settings.DND_START_HOUR <= current_hour or current_hour < settings.DND_END_HOUR:
                return False
        
        # Only call during business hours
        start_hour = int(settings.BUSINESS_HOURS_START.split(':')[0])
        end_hour = int(settings.BUSINESS_HOURS_END.split(':')[0])
        
        return start_hour <= current_hour < end_hour
    
    async def cleanup_old_data(self):
        """Clean up old data based on retention policy."""
        try:
            logger.info("Starting database cleanup")
            
            db = next(get_db())
            cutoff_date = datetime.utcnow() - timedelta(days=settings.DATA_RETENTION_DAYS)
            
            # Delete old conversations
            old_conversations = db.query(Conversation).filter(
                Conversation.created_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"Database cleanup completed - removed {old_conversations} old conversations")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
    
    async def schedule_campaign(
        self,
        campaign_id: int,
        start_time: datetime,
        customer_ids: List[int]
    ):
        """
        Schedule a specific campaign to run at a given time.
        
        Args:
            campaign_id: ID of campaign to run
            start_time: When to start the campaign
            customer_ids: List of customer IDs to target
        """
        job_id = f"campaign_{campaign_id}_{start_time.timestamp()}"
        
        self.scheduler.add_job(
            self._run_specific_campaign,
            DateTrigger(run_date=start_time),
            args=[campaign_id, customer_ids],
            id=job_id,
            name=f"Campaign {campaign_id}"
        )
        
        logger.info(f"Scheduled campaign {campaign_id} for {start_time}")
    
    async def _run_specific_campaign(self, campaign_id: int, customer_ids: List[int]):
        """Run a specific campaign for given customers."""
        try:
            db = next(get_db())
            
            customers = db.query(Customer).filter(
                Customer.id.in_(customer_ids),
                Customer.opt_out_calls == False
            ).all()
            
            await self._execute_promotional_campaign(customers, db)
            
            # Update campaign status
            campaign = db.query(CallCampaign).filter(CallCampaign.id == campaign_id).first()
            if campaign:
                campaign.status = "completed"
                campaign.actual_end = datetime.utcnow()
                campaign.calls_completed = len(customers)
                db.commit()
            
            db.close()
            logger.info(f"Completed specific campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error running specific campaign {campaign_id}: {e}")
