"""
Report Generator for TwistyVoice

This module generates and sends reports to salon managers:
- Daily activity summaries
- Weekly performance reports
- Campaign analytics
- Customer insights
"""

import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import csv
import io

from sqlalchemy.orm import Session
from jinja2 import Template

from models.database import Customer, Conversation, Booking, Promotion, CallCampaign
from core.conversation_tracker import ConversationTracker
from core.promotion_engine import PromotionEngine
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ReportGenerator:
    """
    Generates and sends reports to salon management.
    
    This class creates various types of reports including daily summaries,
    weekly analytics, and campaign performance reports.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.conversation_tracker = ConversationTracker(db)
        self.promotion_engine = PromotionEngine(db)
    
    async def generate_daily_report(self, report_date: Optional[datetime] = None) -> Dict:
        """
        Generate daily activity report.
        
        Args:
            report_date: Date to generate report for (defaults to yesterday)
            
        Returns:
            Dictionary containing report data
        """
        if not report_date:
            report_date = datetime.utcnow() - timedelta(days=1)
        
        start_date = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        # Get conversations for the day
        conversations = self.db.query(Conversation).filter(
            Conversation.created_at.between(start_date, end_date)
        ).all()
        
        # Get bookings for the day
        bookings = self.db.query(Booking).filter(
            Booking.created_at.between(start_date, end_date)
        ).all()
        
        # Calculate metrics
        total_calls = len(conversations)
        answered_calls = len([c for c in conversations if c.call_status == "answered"])
        interested_responses = len([c for c in conversations if c.customer_response == "interested"])
        booked_responses = len([c for c in conversations if c.customer_response == "booked"])
        
        # Revenue from AI-generated bookings
        ai_bookings = [b for b in bookings if b.created_via == "voice_call"]
        ai_revenue = sum(b.price for b in ai_bookings)
        
        report_data = {
            "date": report_date.strftime("%Y-%m-%d"),
            "total_calls": total_calls,
            "answered_calls": answered_calls,
            "interested_responses": interested_responses,
            "bookings_generated": len(ai_bookings),
            "revenue_generated": ai_revenue,
            "answer_rate": answered_calls / total_calls if total_calls > 0 else 0,
            "booking_rate": len(ai_bookings) / answered_calls if answered_calls > 0 else 0,
            "avg_call_duration": sum(c.call_duration or 0 for c in conversations) / answered_calls if answered_calls > 0 else 0,
            "conversations": conversations,
            "bookings": ai_bookings
        }
        
        logger.info(f"Generated daily report for {report_date.strftime('%Y-%m-%d')}")
        return report_data
    
    async def generate_weekly_report(self, week_start: Optional[datetime] = None) -> Dict:
        """
        Generate weekly performance report.
        
        Args:
            week_start: Start of week to report on (defaults to last Monday)
            
        Returns:
            Dictionary containing weekly report data
        """
        if not week_start:
            today = datetime.utcnow().date()
            days_since_monday = today.weekday()
            week_start = datetime.combine(
                today - timedelta(days=days_since_monday + 7),
                datetime.min.time()
            )
        
        week_end = week_start + timedelta(days=7)
        
        # Get weekly analytics
        analytics = self.conversation_tracker.get_call_analytics(week_start, week_end)
        
        # Get bookings for the week
        bookings = self.db.query(Booking).filter(
            Booking.created_at.between(week_start, week_end),
            Booking.created_via == "voice_call"
        ).all()
        
        # Get promotion performance
        promotions = self.db.query(Promotion).filter(
            Promotion.is_active == True
        ).all()
        
        promotion_performance = []
        for promotion in promotions:
            perf = self.promotion_engine.get_promotion_performance(promotion.id)
            perf["promotion_name"] = promotion.name
            promotion_performance.append(perf)
        
        # Customer insights
        new_customers = self.db.query(Customer).filter(
            Customer.created_at.between(week_start, week_end)
        ).count()
        
        returning_customers = len([b for b in bookings if self._is_returning_customer(b.customer_id)])
        
        report_data = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "analytics": analytics,
            "bookings": bookings,
            "total_revenue": sum(b.price for b in bookings),
            "promotion_performance": promotion_performance,
            "new_customers": new_customers,
            "returning_customers": returning_customers,
            "customer_retention_rate": returning_customers / len(bookings) if bookings else 0
        }
        
        logger.info(f"Generated weekly report for week starting {week_start.strftime('%Y-%m-%d')}")
        return report_data
    
    def _is_returning_customer(self, customer_id: int) -> bool:
        """Check if customer is returning (has previous bookings)."""
        previous_bookings = self.db.query(Booking).filter(
            Booking.customer_id == customer_id,
            Booking.status == "completed"
        ).count()
        return previous_bookings > 1
    
    async def generate_campaign_report(self, campaign_id: int) -> Dict:
        """
        Generate report for a specific campaign.
        
        Args:
            campaign_id: ID of campaign to report on
            
        Returns:
            Dictionary containing campaign report data
        """
        campaign = self.db.query(CallCampaign).filter(
            CallCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Get conversations for this campaign
        conversations = self.db.query(Conversation).filter(
            Conversation.promotion_id == campaign.promotion_id,
            Conversation.created_at.between(campaign.actual_start or campaign.scheduled_start, 
                                          campaign.actual_end or datetime.utcnow())
        ).all()
        
        # Get bookings generated by this campaign
        booking_conversations = [c.id for c in conversations if c.customer_response == "booked"]
        bookings = self.db.query(Booking).filter(
            Booking.conversation_id.in_(booking_conversations)
        ).all()
        
        report_data = {
            "campaign": campaign,
            "conversations": conversations,
            "bookings": bookings,
            "total_revenue": sum(b.price for b in bookings),
            "roi": self._calculate_campaign_roi(campaign, bookings),
            "performance_metrics": self._calculate_campaign_metrics(conversations)
        }
        
        return report_data
    
    def _calculate_campaign_roi(self, campaign: CallCampaign, bookings: List[Booking]) -> float:
        """Calculate return on investment for a campaign."""
        revenue = sum(b.price for b in bookings)
        # Estimate campaign cost (simplified)
        estimated_cost = len(bookings) * 2.0  # $2 per call estimate
        return (revenue - estimated_cost) / estimated_cost if estimated_cost > 0 else 0
    
    def _calculate_campaign_metrics(self, conversations: List[Conversation]) -> Dict:
        """Calculate performance metrics for a campaign."""
        total_calls = len(conversations)
        if total_calls == 0:
            return {}
        
        answered = len([c for c in conversations if c.call_status == "answered"])
        interested = len([c for c in conversations if c.customer_response == "interested"])
        booked = len([c for c in conversations if c.customer_response == "booked"])
        
        return {
            "total_calls": total_calls,
            "answer_rate": answered / total_calls,
            "interest_rate": interested / answered if answered > 0 else 0,
            "booking_rate": booked / answered if answered > 0 else 0,
            "conversion_rate": booked / total_calls
        }
    
    async def send_daily_report_email(self, report_date: Optional[datetime] = None):
        """
        Send daily report via email.
        
        Args:
            report_date: Date to generate report for
        """
        try:
            report_data = await self.generate_daily_report(report_date)
            
            # Generate HTML email content
            html_content = self._generate_daily_email_html(report_data)
            
            # Generate CSV attachment
            csv_content = self._generate_daily_csv(report_data)
            
            # Send email
            await self._send_email(
                subject=f"TwistyVoice Daily Report - {report_data['date']}",
                html_content=html_content,
                attachments=[("daily_report.csv", csv_content)]
            )
            
            logger.info(f"Sent daily report email for {report_data['date']}")
            
        except Exception as e:
            logger.error(f"Error sending daily report email: {e}")
    
    async def send_weekly_report_email(self, week_start: Optional[datetime] = None):
        """
        Send weekly report via email.
        
        Args:
            week_start: Start of week to report on
        """
        try:
            report_data = await self.generate_weekly_report(week_start)
            
            # Generate HTML email content
            html_content = self._generate_weekly_email_html(report_data)
            
            # Generate CSV attachment
            csv_content = self._generate_weekly_csv(report_data)
            
            # Send email
            await self._send_email(
                subject=f"TwistyVoice Weekly Report - Week of {report_data['week_start']}",
                html_content=html_content,
                attachments=[("weekly_report.csv", csv_content)]
            )
            
            logger.info(f"Sent weekly report email for week starting {report_data['week_start']}")
            
        except Exception as e:
            logger.error(f"Error sending weekly report email: {e}")
    
    def _generate_daily_email_html(self, report_data: Dict) -> str:
        """Generate HTML content for daily report email."""
        template = Template("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .metrics { display: flex; justify-content: space-around; margin: 20px 0; }
                .metric { text-align: center; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
                .metric-value { font-size: 24px; font-weight: bold; color: #4CAF50; }
                .metric-label { font-size: 14px; color: #666; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>TwistyVoice Daily Report</h1>
                <h2>{{ report_data.date }}</h2>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{{ report_data.total_calls }}</div>
                    <div class="metric-label">Total Calls</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ "%.1f"|format(report_data.answer_rate * 100) }}%</div>
                    <div class="metric-label">Answer Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ report_data.bookings_generated }}</div>
                    <div class="metric-label">Bookings Generated</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${{ "%.2f"|format(report_data.revenue_generated) }}</div>
                    <div class="metric-label">Revenue Generated</div>
                </div>
            </div>
            
            <h3>Recent Bookings</h3>
            <table>
                <tr>
                    <th>Customer</th>
                    <th>Service</th>
                    <th>Appointment Time</th>
                    <th>Price</th>
                </tr>
                {% for booking in report_data.bookings %}
                <tr>
                    <td>{{ booking.customer.first_name }} {{ booking.customer.last_name }}</td>
                    <td>{{ booking.service_name }}</td>
                    <td>{{ booking.appointment_datetime.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>${{ "%.2f"|format(booking.price) }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """)
        
        return template.render(report_data=report_data)
    
    def _generate_weekly_email_html(self, report_data: Dict) -> str:
        """Generate HTML content for weekly report email."""
        # Similar to daily but with weekly metrics
        # Implementation would be similar to daily but with more comprehensive data
        return f"<h1>Weekly Report for {report_data['week_start']} to {report_data['week_end']}</h1>"
    
    def _generate_daily_csv(self, report_data: Dict) -> str:
        """Generate CSV content for daily report."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write summary metrics
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Date", report_data["date"]])
        writer.writerow(["Total Calls", report_data["total_calls"]])
        writer.writerow(["Answered Calls", report_data["answered_calls"]])
        writer.writerow(["Answer Rate", f"{report_data['answer_rate']:.2%}"])
        writer.writerow(["Bookings Generated", report_data["bookings_generated"]])
        writer.writerow(["Revenue Generated", f"${report_data['revenue_generated']:.2f}"])
        writer.writerow([])
        
        # Write booking details
        writer.writerow(["Booking Details"])
        writer.writerow(["Customer", "Service", "Appointment Time", "Price"])
        for booking in report_data["bookings"]:
            writer.writerow([
                f"{booking.customer.first_name} {booking.customer.last_name}",
                booking.service_name,
                booking.appointment_datetime.strftime('%Y-%m-%d %H:%M'),
                f"${booking.price:.2f}"
            ])
        
        return output.getvalue()
    
    def _generate_weekly_csv(self, report_data: Dict) -> str:
        """Generate CSV content for weekly report."""
        # Similar implementation for weekly data
        return "Weekly CSV data would go here"
    
    async def _send_email(
        self,
        subject: str,
        html_content: str,
        attachments: Optional[List[tuple]] = None
    ):
        """
        Send email with HTML content and optional attachments.
        
        Args:
            subject: Email subject
            html_content: HTML email content
            attachments: List of (filename, content) tuples
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USERNAME
            msg['To'] = settings.MANAGER_EMAIL
            msg['Subject'] = subject
            
            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add attachments
            if attachments:
                for filename, content in attachments:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(content.encode())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(settings.SMTP_USERNAME, settings.MANAGER_EMAIL, text)
            server.quit()
            
            logger.info(f"Email sent successfully: {subject}")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
