"""
CSV Data Connector for TwistyVoice

This module handles data management using CSV files instead of Square API:
- Customer data management from CSV
- Simple booking management
- Service catalog from CSV
"""

import logging
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Customer(BaseModel):
    """Customer data model."""
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    total_visits: int = 0
    total_spent: float = 0.0
    preferred_services: List[str] = []
    visit_frequency: str = "monthly"
    preferred_stylist: Optional[str] = None
    opt_out_calls: bool = False
    opt_out_sms: bool = False
    preferred_contact_time: str = "afternoon"


class Booking(BaseModel):
    """Booking data model."""
    id: Optional[str] = None
    customer_id: Optional[str] = None
    service_name: str
    stylist_name: Optional[str] = None
    appointment_date: str
    appointment_time: str
    duration_minutes: int = 60
    status: str = "confirmed"
    customer_note: Optional[str] = None
    created_at: Optional[str] = None


class Service(BaseModel):
    """Service catalog model."""
    id: str
    name: str
    description: Optional[str] = None
    duration_minutes: int = 60
    price: float = 0.0
    category: Optional[str] = None


class CSVDataConnector:
    """CSV-based data connector for customer and booking management."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.customers_file = self.data_dir / "customers.csv"
        self.bookings_file = self.data_dir / "bookings.csv"
        self.services_file = self.data_dir / "services.csv"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize CSV files if they don't exist
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize CSV files with headers if they don't exist."""
        
        # Initialize customers.csv
        if not self.customers_file.exists():
            customer_headers = [
                'id', 'first_name', 'last_name', 'phone_number', 'email',
                'total_visits', 'total_spent', 'preferred_services',
                'visit_frequency', 'preferred_stylist', 'opt_out_calls',
                'opt_out_sms', 'preferred_contact_time'
            ]
            with open(self.customers_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=customer_headers)
                writer.writeheader()
        
        # Initialize bookings.csv
        if not self.bookings_file.exists():
            booking_headers = [
                'id', 'customer_id', 'service_name', 'stylist_name',
                'appointment_date', 'appointment_time', 'duration_minutes',
                'status', 'customer_note', 'created_at'
            ]
            with open(self.bookings_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=booking_headers)
                writer.writeheader()
        
        # Initialize services.csv
        if not self.services_file.exists():
            self._create_sample_services()
    
    def _create_sample_services(self):
        """Create sample services CSV file."""
        sample_services = [
            {
                'id': 'svc_001',
                'name': 'Haircut & Style',
                'description': 'Professional cut and styling',
                'duration_minutes': '60',
                'price': '65.00',
                'category': 'cut'
            },
            {
                'id': 'svc_002',
                'name': 'Color Treatment',
                'description': 'Full color treatment and styling',
                'duration_minutes': '120',
                'price': '120.00',
                'category': 'color'
            },
            {
                'id': 'svc_003',
                'name': 'Braids',
                'description': 'Various braiding styles',
                'duration_minutes': '180',
                'price': '85.00',
                'category': 'braids'
            },
            {
                'id': 'svc_004',
                'name': 'Deep Conditioning',
                'description': 'Intensive hair treatment',
                'duration_minutes': '45',
                'price': '45.00',
                'category': 'treatment'
            },
            {
                'id': 'svc_005',
                'name': 'Wash & Set',
                'description': 'Wash, condition, and style',
                'duration_minutes': '90',
                'price': '55.00',
                'category': 'styling'
            }
        ]
        
        fieldnames = ['id', 'name', 'description', 'duration_minutes', 'price', 'category']
        
        with open(self.services_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_services)
        
        logger.info(f"Created sample services file: {self.services_file}")
    
    async def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number."""
        try:
            with open(self.customers_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['phone_number'] == phone_number:
                        # Parse preferred_services if it's a JSON string
                        preferred_services = []
                        if row.get('preferred_services'):
                            try:
                                preferred_services = json.loads(row['preferred_services'])
                            except json.JSONDecodeError:
                                preferred_services = row['preferred_services'].split(',')
                        
                        return Customer(
                            id=row['id'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            phone_number=row['phone_number'],
                            email=row.get('email', ''),
                            total_visits=int(row.get('total_visits', 0)),
                            total_spent=float(row.get('total_spent', 0.0)),
                            preferred_services=preferred_services,
                            visit_frequency=row.get('visit_frequency', 'monthly'),
                            preferred_stylist=row.get('preferred_stylist', ''),
                            opt_out_calls=row.get('opt_out_calls', '').lower() == 'true',
                            opt_out_sms=row.get('opt_out_sms', '').lower() == 'true',
                            preferred_contact_time=row.get('preferred_contact_time', 'afternoon')
                        )
        except FileNotFoundError:
            logger.error(f"Customers file not found: {self.customers_file}")
        except Exception as e:
            logger.error(f"Error reading customer data: {e}")
        
        return None
    
    async def get_bookings(self, customer_id: Optional[str] = None, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Booking]:
        """Get bookings, optionally filtered by customer and date range."""
        bookings = []
        
        try:
            with open(self.bookings_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter by customer if specified
                    if customer_id and row['customer_id'] != customer_id:
                        continue
                    
                    # Filter by date range if specified
                    if start_date or end_date:
                        booking_date = datetime.strptime(row['appointment_date'], '%Y-%m-%d')
                        if start_date and booking_date < start_date:
                            continue
                        if end_date and booking_date > end_date:
                            continue
                    
                    bookings.append(Booking(
                        id=row['id'],
                        customer_id=row['customer_id'],
                        service_name=row['service_name'],
                        stylist_name=row.get('stylist_name', ''),
                        appointment_date=row['appointment_date'],
                        appointment_time=row['appointment_time'],
                        duration_minutes=int(row.get('duration_minutes', 60)),
                        status=row.get('status', 'confirmed'),
                        customer_note=row.get('customer_note', ''),
                        created_at=row.get('created_at', '')
                    ))
        except FileNotFoundError:
            logger.info(f"Bookings file not found: {self.bookings_file}")
        except Exception as e:
            logger.error(f"Error reading booking data: {e}")
        
        return bookings
    
    async def create_booking(self, booking_data: Dict[str, Any]) -> Optional[str]:
        """Create a new booking and return the booking ID."""
        try:
            # Generate a simple booking ID
            booking_id = f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            booking_row = {
                'id': booking_id,
                'customer_id': booking_data.get('customer_id', ''),
                'service_name': booking_data.get('service_name', ''),
                'stylist_name': booking_data.get('stylist_name', ''),
                'appointment_date': booking_data.get('appointment_date', ''),
                'appointment_time': booking_data.get('appointment_time', ''),
                'duration_minutes': booking_data.get('duration_minutes', 60),
                'status': booking_data.get('status', 'confirmed'),
                'customer_note': booking_data.get('customer_note', ''),
                'created_at': datetime.now().isoformat()
            }
            
            # Read existing bookings
            existing_bookings = []
            if self.bookings_file.exists():
                with open(self.bookings_file, 'r', newline='', encoding='utf-8') as f:
                    existing_bookings = list(csv.DictReader(f))
            
            # Append new booking
            with open(self.bookings_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'id', 'customer_id', 'service_name', 'stylist_name',
                    'appointment_date', 'appointment_time', 'duration_minutes',
                    'status', 'customer_note', 'created_at'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_bookings)
                writer.writerow(booking_row)
            
            logger.info(f"Created booking: {booking_id}")
            return booking_id
            
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return None
    
    async def get_catalog_services(self) -> List[Service]:
        """Get available services from CSV."""
        services = []
        
        try:
            with open(self.services_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    services.append(Service(
                        id=row['id'],
                        name=row['name'],
                        description=row.get('description', ''),
                        duration_minutes=int(row.get('duration_minutes', 60)),
                        price=float(row.get('price', 0.0)),
                        category=row.get('category', '')
                    ))
        except FileNotFoundError:
            logger.error(f"Services file not found: {self.services_file}")
        except Exception as e:
            logger.error(f"Error reading services data: {e}")
        
        return services
    
    async def close(self):
        """Close connections (no-op for CSV connector)."""
        pass
