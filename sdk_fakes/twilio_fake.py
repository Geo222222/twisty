"""
Fake Twilio SDK implementation for portfolio demos.

This module provides a mock Twilio client that simulates SMS and voice calls
without requiring real Twilio credentials or making actual API calls.
"""

import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class FakeCall:
    """Mock Twilio Call object."""
    
    def __init__(self, to: str, from_: str, url: str):
        self.sid = f"CA{uuid4().hex[:32]}"
        self.to = to
        self.from_ = from_
        self.url = url
        self.status = "queued"
        self.direction = "outbound-api"
        self.date_created = datetime.utcnow()
        self.duration = None
        self.price = None
        
        # Simulate call progression
        self._simulate_call()
    
    def _simulate_call(self):
        """Simulate realistic call progression."""
        # Simulate different call outcomes
        outcomes = [
            ("completed", 45, "answered"),
            ("completed", 0, "no-answer"), 
            ("busy", 0, "busy"),
            ("failed", 0, "failed"),
            ("completed", 120, "answered")
        ]
        
        outcome = random.choice(outcomes)
        self.status = outcome[0]
        self.duration = outcome[1] if outcome[1] > 0 else None
        
        logger.info(f"📞 Fake call to {self.to}: {outcome[2]} (duration: {self.duration}s)")


class FakeMessage:
    """Mock Twilio Message object."""
    
    def __init__(self, to: str, from_: str, body: str):
        self.sid = f"SM{uuid4().hex[:32]}"
        self.to = to
        self.from_ = from_
        self.body = body
        self.status = "queued"
        self.direction = "outbound-api"
        self.date_created = datetime.utcnow()
        self.price = None
        self.error_code = None
        self.error_message = None
        
        # Simulate message delivery
        self._simulate_delivery()
    
    def _simulate_delivery(self):
        """Simulate realistic message delivery."""
        # Most messages succeed, some fail
        if random.random() < 0.95:
            self.status = "delivered"
            logger.info(f"📱 Fake SMS to {self.to}: delivered")
        else:
            self.status = "failed"
            self.error_code = 30008
            self.error_message = "Unknown destination handset"
            logger.warning(f"📱 Fake SMS to {self.to}: failed")


class FakeCallsResource:
    """Mock Twilio Calls resource."""
    
    def __init__(self):
        self.calls: List[FakeCall] = []
    
    def create(self, to: str, from_: str, url: str, **kwargs) -> FakeCall:
        """Create a fake call."""
        call = FakeCall(to, from_, url)
        self.calls.append(call)
        return call
    
    def list(self, limit: int = 50) -> List[FakeCall]:
        """List recent fake calls."""
        return self.calls[-limit:]


class FakeMessagesResource:
    """Mock Twilio Messages resource."""
    
    def __init__(self):
        self.messages: List[FakeMessage] = []
    
    def create(self, to: str, from_: str, body: str, **kwargs) -> FakeMessage:
        """Create a fake message."""
        message = FakeMessage(to, from_, body)
        self.messages.append(message)
        return message
    
    def list(self, limit: int = 50) -> List[FakeMessage]:
        """List recent fake messages."""
        return self.messages[-limit:]


class FakeTwilioClient:
    """
    Mock Twilio Client that simulates the real Twilio REST API.
    
    This fake client provides the same interface as the real Twilio client
    but doesn't make actual API calls or require real credentials.
    """
    
    def __init__(self, account_sid: str = "fake_sid", auth_token: str = "fake_token"):
        self.account_sid = account_sid
        self.auth_token = auth_token
        
        # Initialize fake resources
        self.calls = FakeCallsResource()
        self.messages = FakeMessagesResource()
        
        logger.info("🎭 Initialized Fake Twilio Client (no real API calls will be made)")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def get_twilio_client(account_sid: str = None, auth_token: str = None) -> FakeTwilioClient:
    """
    Factory function to get a Twilio client.
    
    In demo mode, this returns a fake client.
    In production, this would return the real Twilio client.
    """
    return FakeTwilioClient(account_sid or "fake_sid", auth_token or "fake_token")


# Example usage for testing
if __name__ == "__main__":
    # Demo the fake Twilio client
    client = get_twilio_client()
    
    # Send a fake SMS
    message = client.messages.create(
        to="+1234567890",
        from_="+1987654321", 
        body="Hello from TwistyVoice! This is a fake SMS for demo purposes."
    )
    print(f"Message SID: {message.sid}, Status: {message.status}")
    
    # Make a fake call
    call = client.calls.create(
        to="+1234567890",
        from_="+1987654321",
        url="http://demo.twilio.com/docs/voice.xml"
    )
    print(f"Call SID: {call.sid}, Status: {call.status}")
