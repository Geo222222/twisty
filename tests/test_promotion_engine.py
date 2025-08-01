"""
Tests for the Promotion Engine module.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the settings to avoid validation errors
import unittest.mock
with unittest.mock.patch.dict(os.environ, {
    'SQUARE_APPLICATION_ID': 'test',
    'SQUARE_ACCESS_TOKEN': 'test',
    'TWILIO_ACCOUNT_SID': 'test',
    'TWILIO_AUTH_TOKEN': 'test',
    'TWILIO_PHONE_NUMBER': 'test',
    'SMTP_USERNAME': 'test',
    'SMTP_PASSWORD': 'test',
    'MANAGER_EMAIL': 'test@test.com',
    'SALON_PHONE': 'test',
    'SALON_ADDRESS': 'test',
    'SECRET_KEY': 'test',
    'ENCRYPTION_KEY': 'test' * 4  # 32 characters
}):
    from models.database import Base, Customer, Promotion
    from core.promotion_engine import PromotionEngine, CustomerSegment


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer for testing."""
    customer = Customer(
        first_name="Jane",
        last_name="Doe",
        phone_number="+1234567890",
        email="jane.doe@example.com",
        total_visits=5,
        total_spent=250.0,
        last_visit_date=datetime.utcnow() - timedelta(days=45)
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_promotion(db_session):
    """Create a sample promotion for testing."""
    promotion = Promotion(
        name="Test Promotion",
        description="20% off all services",
        discount_percentage=20.0,
        target_customer_segments='["regular_customer"]',
        min_days_since_visit=30,
        max_days_since_visit=90,
        start_date=datetime.utcnow() - timedelta(days=10),
        end_date=datetime.utcnow() + timedelta(days=30),
        max_uses=100,
        current_uses=0,
        is_active=True
    )
    db_session.add(promotion)
    db_session.commit()
    db_session.refresh(promotion)
    return promotion


def test_analyze_customer_segment(db_session, sample_customer):
    """Test customer segment analysis."""
    engine = PromotionEngine(db_session)
    segments = engine.analyze_customer_segment(sample_customer)
    
    assert CustomerSegment.REGULAR_CUSTOMER in segments
    assert len(segments) > 0


def test_get_eligible_promotions(db_session, sample_customer, sample_promotion):
    """Test getting eligible promotions for a customer."""
    engine = PromotionEngine(db_session)
    eligible_promotions = engine.get_eligible_promotions(sample_customer)
    
    assert len(eligible_promotions) == 1
    assert eligible_promotions[0].id == sample_promotion.id


def test_select_best_promotion(db_session, sample_customer, sample_promotion):
    """Test selecting the best promotion for a customer."""
    engine = PromotionEngine(db_session)
    best_promotion = engine.select_best_promotion(sample_customer)
    
    assert best_promotion is not None
    assert best_promotion.id == sample_promotion.id


def test_promotion_scoring(db_session, sample_customer, sample_promotion):
    """Test promotion scoring algorithm."""
    engine = PromotionEngine(db_session)
    score = engine._calculate_promotion_score(sample_customer, sample_promotion)
    
    assert score > 0
    assert isinstance(score, float)


def test_customer_eligibility_days_since_visit(db_session):
    """Test customer eligibility based on days since last visit."""
    # Create customer with recent visit (should not be eligible)
    recent_customer = Customer(
        first_name="Recent",
        last_name="Customer",
        phone_number="+1111111111",
        total_visits=3,
        last_visit_date=datetime.utcnow() - timedelta(days=10)
    )
    db_session.add(recent_customer)
    
    # Create promotion requiring 30+ days since visit
    promotion = Promotion(
        name="Comeback Promotion",
        discount_percentage=15.0,
        min_days_since_visit=30,
        start_date=datetime.utcnow() - timedelta(days=5),
        end_date=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db_session.add(promotion)
    db_session.commit()
    
    engine = PromotionEngine(db_session)
    
    # Recent customer should not be eligible
    assert not engine._is_customer_eligible(recent_customer, promotion)


def test_new_customer_segment():
    """Test new customer segment identification."""
    new_customer = Customer(
        first_name="New",
        last_name="Customer",
        total_visits=0,
        total_spent=0.0
    )
    
    # Mock database session
    class MockDB:
        pass
    
    engine = PromotionEngine(MockDB())
    segments = engine.analyze_customer_segment(new_customer)
    
    assert CustomerSegment.NEW_CUSTOMER in segments


def test_vip_customer_segment():
    """Test VIP customer segment identification."""
    vip_customer = Customer(
        first_name="VIP",
        last_name="Customer",
        total_visits=25,
        total_spent=1500.0
    )
    
    # Mock database session
    class MockDB:
        pass
    
    engine = PromotionEngine(MockDB())
    segments = engine.analyze_customer_segment(vip_customer)
    
    assert CustomerSegment.VIP_CUSTOMER in segments


def test_lapsed_customer_segment():
    """Test lapsed customer segment identification."""
    lapsed_customer = Customer(
        first_name="Lapsed",
        last_name="Customer",
        total_visits=8,
        total_spent=400.0,
        last_visit_date=datetime.utcnow() - timedelta(days=120)
    )
    
    # Mock database session
    class MockDB:
        pass
    
    engine = PromotionEngine(MockDB())
    segments = engine.analyze_customer_segment(lapsed_customer)
    
    assert CustomerSegment.LAPSED_CUSTOMER in segments


if __name__ == "__main__":
    pytest.main([__file__])
