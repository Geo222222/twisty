"""
Square API Connector for TwistyVoice

This module handles all interactions with the Square API including:
- Customer data retrieval and management
- Booking creation and management
- Payment processing (future)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SquareCustomer(BaseModel):
    """Square customer data model."""
    id: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SquareBooking(BaseModel):
    """Square booking data model."""
    id: str
    appointment_segments: List[Dict]
    customer_id: Optional[str] = None
    customer_note: Optional[str] = None
    seller_note: Optional[str] = None
    status: str
    created_at: str
    updated_at: str


class SquareService(BaseModel):
    """Square service/catalog item model."""
    id: str
    name: str
    description: Optional[str] = None
    price_money: Optional[Dict] = None
    duration: Optional[int] = None  # in minutes


class SquareConnector:
    """
    Square API connector for customer and booking management.
    
    This class provides methods to interact with Square's APIs for:
    - Retrieving customer information
    - Managing bookings and appointments
    - Fetching service catalog
    """
    
    def __init__(self):
        self.base_url = self._get_base_url()
        self.headers = {
            "Square-Version": "2023-10-18",
            "Authorization": f"Bearer {settings.SQUARE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_base_url(self) -> str:
        """Get the appropriate Square API base URL."""
        if settings.SQUARE_ENVIRONMENT == "production":
            return "https://connect.squareup.com"
        return "https://connect.squareupsandbox.com"
    
    async def get_customers(
        self, 
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict:
        """
        Retrieve customers from Square.
        
        Args:
            limit: Maximum number of customers to retrieve
            cursor: Pagination cursor for next page
            
        Returns:
            Dictionary containing customers and pagination info
        """
        try:
            url = f"{self.base_url}/v2/customers"
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('customers', []))} customers from Square")
            
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Error retrieving customers from Square: {e}")
            raise
    
    async def get_customer_by_id(self, customer_id: str) -> Optional[SquareCustomer]:
        """
        Retrieve a specific customer by ID.
        
        Args:
            customer_id: Square customer ID
            
        Returns:
            SquareCustomer object or None if not found
        """
        try:
            url = f"{self.base_url}/v2/customers/{customer_id}"
            
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            customer_data = data.get("customer")
            
            if customer_data:
                return SquareCustomer(**customer_data)
            
            return None
            
        except httpx.HTTPError as e:
            logger.error(f"Error retrieving customer {customer_id}: {e}")
            return None
    
    async def search_customers(
        self, 
        phone_number: Optional[str] = None,
        email: Optional[str] = None
    ) -> List[SquareCustomer]:
        """
        Search for customers by phone or email.
        
        Args:
            phone_number: Customer phone number
            email: Customer email address
            
        Returns:
            List of matching SquareCustomer objects
        """
        try:
            url = f"{self.base_url}/v2/customers/search"
            
            query = {}
            if phone_number:
                query["phone_number"] = {"exact": phone_number}
            if email:
                query["email_address"] = {"exact": email}
            
            payload = {
                "query": query,
                "limit": 100
            }
            
            response = await self.client.post(
                url, 
                headers=self.headers, 
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            customers = []
            
            for customer_data in data.get("customers", []):
                customers.append(SquareCustomer(**customer_data))
            
            logger.info(f"Found {len(customers)} customers matching search criteria")
            return customers
            
        except httpx.HTTPError as e:
            logger.error(f"Error searching customers: {e}")
            return []
    
    async def get_bookings(
        self,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SquareBooking]:
        """
        Retrieve bookings within a date range.
        
        Args:
            start_at: Start date for booking search
            end_at: End date for booking search
            limit: Maximum number of bookings to retrieve
            
        Returns:
            List of SquareBooking objects
        """
        try:
            url = f"{self.base_url}/v2/bookings"
            
            # Default to next 30 days if no dates provided
            if not start_at:
                start_at = datetime.utcnow()
            if not end_at:
                end_at = start_at + timedelta(days=30)
            
            params = {
                "start_at_min": start_at.isoformat() + "Z",
                "start_at_max": end_at.isoformat() + "Z",
                "limit": limit
            }
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            bookings = []
            
            for booking_data in data.get("bookings", []):
                bookings.append(SquareBooking(**booking_data))
            
            logger.info(f"Retrieved {len(bookings)} bookings from Square")
            return bookings
            
        except httpx.HTTPError as e:
            logger.error(f"Error retrieving bookings: {e}")
            return []
    
    async def create_booking(
        self,
        customer_id: str,
        service_id: str,
        start_time: datetime,
        duration_minutes: int,
        team_member_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new booking in Square.
        
        Args:
            customer_id: Square customer ID
            service_id: Square service/catalog item ID
            start_time: Appointment start time
            duration_minutes: Appointment duration
            team_member_id: Optional stylist/team member ID
            
        Returns:
            Booking ID if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/v2/bookings"
            
            appointment_segment = {
                "duration_minutes": duration_minutes,
                "service_variation_id": service_id,
                "start_at": start_time.isoformat() + "Z"
            }
            
            if team_member_id:
                appointment_segment["team_member_id"] = team_member_id
            
            payload = {
                "booking": {
                    "appointment_segments": [appointment_segment],
                    "customer_id": customer_id,
                    "seller_note": "Booked via TwistyVoice AI Assistant"
                }
            }
            
            response = await self.client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            booking_id = data.get("booking", {}).get("id")
            
            if booking_id:
                logger.info(f"Successfully created booking {booking_id}")
                return booking_id
            
            return None
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating booking: {e}")
            return None
    
    async def get_catalog_services(self) -> List[SquareService]:
        """
        Retrieve available services from Square catalog.
        
        Returns:
            List of SquareService objects
        """
        try:
            url = f"{self.base_url}/v2/catalog/list"
            params = {"types": "ITEM"}
            
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            services = []
            
            for item in data.get("objects", []):
                if item.get("type") == "ITEM":
                    item_data = item.get("item_data", {})
                    service = SquareService(
                        id=item["id"],
                        name=item_data.get("name", ""),
                        description=item_data.get("description"),
                    )
                    
                    # Get price from variations if available
                    variations = item_data.get("variations", [])
                    if variations:
                        variation = variations[0]
                        variation_data = variation.get("item_variation_data", {})
                        service.price_money = variation_data.get("price_money")
                    
                    services.append(service)
            
            logger.info(f"Retrieved {len(services)} services from catalog")
            return services
            
        except httpx.HTTPError as e:
            logger.error(f"Error retrieving catalog services: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
