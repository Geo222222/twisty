"""
Fake Square SDK implementation for portfolio demos.

This module provides a mock Square client that simulates customer data
and appointment booking without requiring real Square credentials.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class FakeCustomer:
    """Mock Square Customer object."""
    
    def __init__(self, data: Dict):
        self.id = data.get('id', f"CUST_{uuid4().hex[:16].upper()}")
        self.given_name = data.get('given_name', 'John')
        self.family_name = data.get('family_name', 'Doe')
        self.email_address = data.get('email_address')
        self.phone_number = data.get('phone_number')
        self.created_at = data.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = data.get('updated_at', datetime.utcnow().isoformat())
        self.preferences = data.get('preferences', {})
        self.group_ids = data.get('group_ids', [])


class FakeBooking:
    """Mock Square Booking object."""
    
    def __init__(self, data: Dict):
        self.id = data.get('id', f"BOOK_{uuid4().hex[:16].upper()}")
        self.version = data.get('version', 1)
        self.status = data.get('status', 'ACCEPTED')
        self.created_at = data.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = data.get('updated_at', datetime.utcnow().isoformat())
        self.start_at = data.get('start_at')
        self.location_id = data.get('location_id', 'LOCATION_1')
        self.customer_id = data.get('customer_id')
        self.customer_note = data.get('customer_note', '')
        self.seller_note = data.get('seller_note', '')
        self.appointment_segments = data.get('appointment_segments', [])


class FakeCustomersApi:
    """Mock Square Customers API."""
    
    def __init__(self):
        # Pre-populate with sample customers for demo
        self.customers = [
            FakeCustomer({
                'id': 'CUST_VIP001',
                'given_name': 'Sarah',
                'family_name': 'Johnson',
                'email_address': 'sarah.johnson@email.com',
                'phone_number': '+15551234567',
                'preferences': {'visit_frequency': 'monthly', 'preferred_stylist': 'Maria'}
            }),
            FakeCustomer({
                'id': 'CUST_VIP002', 
                'given_name': 'Emily',
                'family_name': 'Davis',
                'email_address': 'emily.davis@email.com',
                'phone_number': '+15551234568',
                'preferences': {'visit_frequency': 'bi-weekly', 'preferred_stylist': 'Jessica'}
            }),
            FakeCustomer({
                'id': 'CUST_VIP003',
                'given_name': 'Ashley',
                'family_name': 'Wilson',
                'email_address': 'ashley.wilson@email.com', 
                'phone_number': '+15551234569',
                'preferences': {'visit_frequency': 'weekly', 'preferred_stylist': 'Maria'}
            }),
            FakeCustomer({
                'id': 'CUST_REG001',
                'given_name': 'Jennifer',
                'family_name': 'Brown',
                'email_address': 'jennifer.brown@email.com',
                'phone_number': '+15551234570',
                'preferences': {'visit_frequency': 'quarterly', 'preferred_stylist': 'Any'}
            }),
            FakeCustomer({
                'id': 'CUST_REG002',
                'given_name': 'Michelle',
                'family_name': 'Taylor',
                'email_address': 'michelle.taylor@email.com',
                'phone_number': '+15551234571',
                'preferences': {'visit_frequency': 'monthly', 'preferred_stylist': 'Jessica'}
            })
        ]
        
        logger.info(f"🎭 Initialized Fake Square Customers API with {len(self.customers)} sample customers")
    
    def list_customers(self, cursor: str = None, limit: int = 100, **kwargs) -> Dict:
        """List customers with pagination."""
        start_idx = 0
        if cursor:
            try:
                start_idx = int(cursor)
            except ValueError:
                start_idx = 0
        
        end_idx = min(start_idx + limit, len(self.customers))
        customers_page = self.customers[start_idx:end_idx]
        
        result = {
            'customers': [
                {
                    'id': customer.id,
                    'given_name': customer.given_name,
                    'family_name': customer.family_name,
                    'email_address': customer.email_address,
                    'phone_number': customer.phone_number,
                    'created_at': customer.created_at,
                    'updated_at': customer.updated_at,
                    'preferences': customer.preferences,
                    'group_ids': customer.group_ids
                }
                for customer in customers_page
            ]
        }
        
        # Add cursor for next page if there are more customers
        if end_idx < len(self.customers):
            result['cursor'] = str(end_idx)
        
        logger.info(f"📋 Listed {len(customers_page)} fake customers")
        return result
    
    def retrieve_customer(self, customer_id: str) -> Dict:
        """Retrieve a specific customer."""
        customer = next((c for c in self.customers if c.id == customer_id), None)
        if not customer:
            raise Exception(f"Customer {customer_id} not found")
        
        return {
            'customer': {
                'id': customer.id,
                'given_name': customer.given_name,
                'family_name': customer.family_name,
                'email_address': customer.email_address,
                'phone_number': customer.phone_number,
                'created_at': customer.created_at,
                'updated_at': customer.updated_at,
                'preferences': customer.preferences,
                'group_ids': customer.group_ids
            }
        }


class FakeBookingsApi:
    """Mock Square Bookings API."""
    
    def __init__(self):
        self.bookings = []
        logger.info("🎭 Initialized Fake Square Bookings API")
    
    def create_booking(self, body: Dict) -> Dict:
        """Create a new booking."""
        booking_data = body.get('booking', {})
        booking = FakeBooking(booking_data)
        self.bookings.append(booking)
        
        logger.info(f"📅 Created fake booking {booking.id} for customer {booking.customer_id}")
        
        return {
            'booking': {
                'id': booking.id,
                'version': booking.version,
                'status': booking.status,
                'created_at': booking.created_at,
                'updated_at': booking.updated_at,
                'start_at': booking.start_at,
                'location_id': booking.location_id,
                'customer_id': booking.customer_id,
                'customer_note': booking.customer_note,
                'seller_note': booking.seller_note,
                'appointment_segments': booking.appointment_segments
            }
        }
    
    def list_bookings(self, limit: int = 100, **kwargs) -> Dict:
        """List bookings."""
        return {
            'bookings': [
                {
                    'id': booking.id,
                    'version': booking.version,
                    'status': booking.status,
                    'created_at': booking.created_at,
                    'updated_at': booking.updated_at,
                    'start_at': booking.start_at,
                    'location_id': booking.location_id,
                    'customer_id': booking.customer_id,
                    'customer_note': booking.customer_note,
                    'seller_note': booking.seller_note,
                    'appointment_segments': booking.appointment_segments
                }
                for booking in self.bookings[-limit:]
            ]
        }


class FakeSquareClient:
    """
    Mock Square Client that simulates the real Square API.
    
    This fake client provides the same interface as the real Square client
    but doesn't make actual API calls or require real credentials.
    """
    
    def __init__(self, access_token: str = "fake_token", environment: str = "sandbox"):
        self.access_token = access_token
        self.environment = environment
        
        # Initialize fake APIs
        self.customers = FakeCustomersApi()
        self.bookings = FakeBookingsApi()
        
        logger.info("🎭 Initialized Fake Square Client (no real API calls will be made)")


def get_square_client(access_token: str = None, environment: str = "sandbox") -> FakeSquareClient:
    """
    Factory function to get a Square client.
    
    In demo mode, this returns a fake client.
    In production, this would return the real Square client.
    """
    return FakeSquareClient(access_token or "fake_token", environment)


# Example usage for testing
if __name__ == "__main__":
    # Demo the fake Square client
    client = get_square_client()
    
    # List customers
    result = client.customers.list_customers(limit=3)
    print(f"Found {len(result['customers'])} customers")
    
    for customer in result['customers']:
        print(f"- {customer['given_name']} {customer['family_name']} ({customer['phone_number']})")
    
    # Create a booking
    booking_data = {
        'booking': {
            'start_at': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'customer_id': 'CUST_VIP001',
            'customer_note': 'Haircut and color',
            'appointment_segments': [
                {
                    'duration_minutes': 90,
                    'service_variation_id': 'SERVICE_HAIRCUT_COLOR'
                }
            ]
        }
    }
    
    booking_result = client.bookings.create_booking(booking_data)
    print(f"Created booking: {booking_result['booking']['id']}")
