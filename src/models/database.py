"""
Database models and configuration for TwistyVoice.

This module defines all SQLAlchemy models and database configuration.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config.settings import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class Customer(Base):
    """Customer model representing salon customers."""
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, index=True)
    email = Column(String, index=True)
    
    # Customer preferences and history
    preferred_stylist = Column(String)
    preferred_services = Column(Text)  # JSON string
    visit_frequency = Column(String)  # weekly, monthly, quarterly, etc.
    last_visit_date = Column(DateTime)
    total_visits = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    
    # Communication preferences
    opt_out_calls = Column(Boolean, default=False)
    opt_out_sms = Column(Boolean, default=False)
    preferred_contact_time = Column(String)  # morning, afternoon, evening
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="customer")
    bookings = relationship("Booking", back_populates="customer")


class Promotion(Base):
    """Promotion model for managing special offers."""
    
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    
    # Targeting criteria
    target_services = Column(Text)  # JSON string
    target_customer_segments = Column(Text)  # JSON string
    min_days_since_visit = Column(Integer)
    max_days_since_visit = Column(Integer)
    
    # Campaign settings
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Conversation model for tracking customer interactions."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    
    # Call details
    call_type = Column(String)  # promotional, reminder, follow_up
    call_status = Column(String)  # answered, voicemail, busy, failed
    call_duration = Column(Integer)  # seconds
    
    # Interaction details
    customer_response = Column(String)  # interested, not_interested, booked, callback
    notes = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # Technical details
    twilio_call_sid = Column(String)
    recording_url = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="conversations")
    promotion = relationship("Promotion")


class Booking(Base):
    """Booking model for tracking appointments."""
    
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    # External booking details
    external_booking_id = Column(String, unique=True, index=True)
    appointment_datetime = Column(DateTime)
    service_name = Column(String)
    stylist_name = Column(String)
    duration_minutes = Column(Integer)
    price = Column(Float)
    
    # Booking status
    status = Column(String)  # confirmed, cancelled, completed, no_show
    created_via = Column(String)  # voice_call, sms, manual, csv_import
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="bookings")
    conversation = relationship("Conversation")


class CallCampaign(Base):
    """Call campaign model for managing promotional campaigns."""
    
    __tablename__ = "call_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    promotion_id = Column(Integer, ForeignKey("promotions.id"))
    
    # Campaign settings
    target_customer_count = Column(Integer)
    calls_completed = Column(Integer, default=0)
    calls_successful = Column(Integer, default=0)
    bookings_generated = Column(Integer, default=0)
    
    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Status
    status = Column(String)  # scheduled, running, paused, completed, cancelled
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    promotion = relationship("Promotion")


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
