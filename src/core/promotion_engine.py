"""
Promotion Engine for TwistyVoice

This module handles promotion targeting and selection logic:
- Customer segmentation based on visit history
- Promotion matching based on customer preferences
- Campaign optimization and A/B testing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Customer, Promotion, Conversation
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CustomerSegment:
    """Customer segmentation categories."""
    
    NEW_CUSTOMER = "new_customer"
    REGULAR_CUSTOMER = "regular_customer"
    VIP_CUSTOMER = "vip_customer"
    LAPSED_CUSTOMER = "lapsed_customer"
    PRICE_SENSITIVE = "price_sensitive"
    SERVICE_SPECIFIC = "service_specific"


class PromotionEngine:
    """
    Promotion targeting and selection engine.
    
    This class analyzes customer data and selects the most appropriate
    promotions for each customer based on their history, preferences,
    and behavior patterns.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_customer_segment(self, customer: Customer) -> List[str]:
        """
        Analyze customer data to determine their segment(s).
        
        Args:
            customer: Customer object to analyze
            
        Returns:
            List of customer segment identifiers
        """
        segments = []
        
        # Analyze visit frequency
        if customer.total_visits == 0:
            segments.append(CustomerSegment.NEW_CUSTOMER)
        elif customer.total_visits >= 20:
            segments.append(CustomerSegment.VIP_CUSTOMER)
        elif customer.total_visits >= 5:
            segments.append(CustomerSegment.REGULAR_CUSTOMER)
        
        # Analyze recency
        if customer.last_visit_date:
            days_since_visit = (datetime.utcnow() - customer.last_visit_date).days
            
            if days_since_visit > 90:
                segments.append(CustomerSegment.LAPSED_CUSTOMER)
        
        # Analyze spending patterns
        if customer.total_visits > 0:
            avg_spend = customer.total_spent / customer.total_visits
            if avg_spend < 50:  # Configurable threshold
                segments.append(CustomerSegment.PRICE_SENSITIVE)
        
        # Analyze service preferences
        if customer.preferred_services:
            segments.append(CustomerSegment.SERVICE_SPECIFIC)
        
        logger.debug(f"Customer {customer.id} segments: {segments}")
        return segments
    
    def get_eligible_promotions(
        self, 
        customer: Customer,
        active_only: bool = True
    ) -> List[Promotion]:
        """
        Get promotions that the customer is eligible for.
        
        Args:
            customer: Customer to find promotions for
            active_only: Only return active promotions
            
        Returns:
            List of eligible Promotion objects
        """
        query = self.db.query(Promotion)
        
        if active_only:
            query = query.filter(
                Promotion.is_active == True,
                Promotion.start_date <= datetime.utcnow(),
                Promotion.end_date >= datetime.utcnow()
            )
        
        all_promotions = query.all()
        eligible_promotions = []
        
        for promotion in all_promotions:
            if self._is_customer_eligible(customer, promotion):
                eligible_promotions.append(promotion)
        
        logger.info(f"Found {len(eligible_promotions)} eligible promotions for customer {customer.id}")
        return eligible_promotions
    
    def _is_customer_eligible(self, customer: Customer, promotion: Promotion) -> bool:
        """
        Check if a customer is eligible for a specific promotion.
        
        Args:
            customer: Customer to check
            promotion: Promotion to check eligibility for
            
        Returns:
            True if customer is eligible, False otherwise
        """
        # Check usage limits
        if promotion.max_uses and promotion.current_uses >= promotion.max_uses:
            return False
        
        # Check if customer has already used this promotion
        existing_conversation = self.db.query(Conversation).filter(
            Conversation.customer_id == customer.id,
            Conversation.promotion_id == promotion.id,
            Conversation.customer_response.in_(["booked", "interested"])
        ).first()
        
        if existing_conversation:
            return False
        
        # Check days since last visit criteria
        if customer.last_visit_date:
            days_since_visit = (datetime.utcnow() - customer.last_visit_date).days
            
            if promotion.min_days_since_visit and days_since_visit < promotion.min_days_since_visit:
                return False
            
            if promotion.max_days_since_visit and days_since_visit > promotion.max_days_since_visit:
                return False
        
        # Check customer segment targeting
        if promotion.target_customer_segments:
            import json
            target_segments = json.loads(promotion.target_customer_segments)
            customer_segments = self.analyze_customer_segment(customer)
            
            # Customer must match at least one target segment
            if not any(segment in target_segments for segment in customer_segments):
                return False
        
        # Check service targeting
        if promotion.target_services and customer.preferred_services:
            import json
            target_services = json.loads(promotion.target_services)
            customer_services = json.loads(customer.preferred_services)
            
            # Customer must have used at least one target service
            if not any(service in target_services for service in customer_services):
                return False
        
        return True
    
    def select_best_promotion(
        self, 
        customer: Customer,
        eligible_promotions: Optional[List[Promotion]] = None
    ) -> Optional[Promotion]:
        """
        Select the best promotion for a customer using scoring algorithm.
        
        Args:
            customer: Customer to select promotion for
            eligible_promotions: Pre-filtered list of eligible promotions
            
        Returns:
            Best Promotion object or None if no suitable promotion
        """
        if eligible_promotions is None:
            eligible_promotions = self.get_eligible_promotions(customer)
        
        if not eligible_promotions:
            return None
        
        # Score each promotion
        scored_promotions = []
        for promotion in eligible_promotions:
            score = self._calculate_promotion_score(customer, promotion)
            scored_promotions.append((promotion, score))
        
        # Sort by score (highest first)
        scored_promotions.sort(key=lambda x: x[1], reverse=True)
        
        best_promotion = scored_promotions[0][0]
        logger.info(f"Selected promotion '{best_promotion.name}' for customer {customer.id}")
        
        return best_promotion
    
    def _calculate_promotion_score(self, customer: Customer, promotion: Promotion) -> float:
        """
        Calculate a score for how well a promotion matches a customer.
        
        Args:
            customer: Customer to score for
            promotion: Promotion to score
            
        Returns:
            Promotion score (higher is better)
        """
        score = 0.0
        
        # Base score for discount value
        if promotion.discount_percentage:
            score += promotion.discount_percentage * 2  # Weight percentage discounts
        if promotion.discount_amount:
            score += promotion.discount_amount / 10  # Weight dollar discounts
        
        # Bonus for customer segment matching
        customer_segments = self.analyze_customer_segment(customer)
        if promotion.target_customer_segments:
            import json
            target_segments = json.loads(promotion.target_customer_segments)
            
            for segment in customer_segments:
                if segment in target_segments:
                    score += 20  # Bonus for segment match
        
        # Bonus for service preference matching
        if promotion.target_services and customer.preferred_services:
            import json
            target_services = json.loads(promotion.target_services)
            customer_services = json.loads(customer.preferred_services)
            
            matches = sum(1 for service in customer_services if service in target_services)
            score += matches * 15  # Bonus per service match
        
        # Penalty for overused promotions (encourage variety)
        usage_ratio = promotion.current_uses / max(promotion.max_uses or 1000, 1)
        score -= usage_ratio * 10
        
        # Bonus for urgency (ending soon)
        if promotion.end_date:
            days_until_end = (promotion.end_date - datetime.utcnow()).days
            if days_until_end <= 7:
                score += 25  # Urgency bonus
        
        # Bonus for lapsed customers getting win-back offers
        if CustomerSegment.LAPSED_CUSTOMER in customer_segments:
            if "comeback" in promotion.name.lower() or "welcome back" in promotion.name.lower():
                score += 30
        
        logger.debug(f"Promotion '{promotion.name}' scored {score} for customer {customer.id}")
        return score
    
    def get_promotion_performance(self, promotion_id: int) -> Dict:
        """
        Get performance metrics for a specific promotion.
        
        Args:
            promotion_id: ID of promotion to analyze
            
        Returns:
            Dictionary with performance metrics
        """
        conversations = self.db.query(Conversation).filter(
            Conversation.promotion_id == promotion_id
        ).all()
        
        total_calls = len(conversations)
        answered_calls = len([c for c in conversations if c.call_status == "answered"])
        interested_responses = len([c for c in conversations if c.customer_response == "interested"])
        bookings = len([c for c in conversations if c.customer_response == "booked"])
        
        metrics = {
            "total_calls": total_calls,
            "answered_calls": answered_calls,
            "interested_responses": interested_responses,
            "bookings_generated": bookings,
            "answer_rate": answered_calls / total_calls if total_calls > 0 else 0,
            "interest_rate": interested_responses / answered_calls if answered_calls > 0 else 0,
            "booking_rate": bookings / answered_calls if answered_calls > 0 else 0,
            "overall_conversion": bookings / total_calls if total_calls > 0 else 0
        }
        
        return metrics
    
    def get_campaign_recommendations(self, days_ahead: int = 7) -> List[Dict]:
        """
        Generate campaign recommendations for the next period.
        
        Args:
            days_ahead: Number of days to plan ahead
            
        Returns:
            List of campaign recommendation dictionaries
        """
        recommendations = []
        
        # Analyze customer segments that haven't been contacted recently
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        uncontacted_customers = self.db.query(Customer).filter(
            ~Customer.conversations.any(Conversation.created_at > cutoff_date),
            Customer.opt_out_calls == False
        ).all()
        
        # Group by segments
        segment_counts = {}
        for customer in uncontacted_customers:
            segments = self.analyze_customer_segment(customer)
            for segment in segments:
                segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        # Generate recommendations based on segment sizes
        for segment, count in segment_counts.items():
            if count >= 10:  # Minimum viable campaign size
                recommendations.append({
                    "segment": segment,
                    "customer_count": count,
                    "recommended_promotion_type": self._get_recommended_promotion_type(segment),
                    "priority": self._get_campaign_priority(segment, count)
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        
        return recommendations
    
    def _get_recommended_promotion_type(self, segment: str) -> str:
        """Get recommended promotion type for a customer segment."""
        promotion_map = {
            CustomerSegment.NEW_CUSTOMER: "First-time discount",
            CustomerSegment.LAPSED_CUSTOMER: "Welcome back offer",
            CustomerSegment.PRICE_SENSITIVE: "Percentage discount",
            CustomerSegment.VIP_CUSTOMER: "Exclusive service",
            CustomerSegment.REGULAR_CUSTOMER: "Loyalty reward",
            CustomerSegment.SERVICE_SPECIFIC: "Service-specific discount"
        }
        return promotion_map.get(segment, "General promotion")
    
    def _get_campaign_priority(self, segment: str, count: int) -> int:
        """Calculate campaign priority based on segment and size."""
        base_priority = {
            CustomerSegment.LAPSED_CUSTOMER: 100,
            CustomerSegment.VIP_CUSTOMER: 90,
            CustomerSegment.NEW_CUSTOMER: 80,
            CustomerSegment.REGULAR_CUSTOMER: 70,
            CustomerSegment.PRICE_SENSITIVE: 60,
            CustomerSegment.SERVICE_SPECIFIC: 50
        }.get(segment, 40)
        
        # Bonus for larger campaigns
        size_bonus = min(count // 10, 20)
        
        return base_priority + size_bonus
