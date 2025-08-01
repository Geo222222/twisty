#!/usr/bin/env python3
"""
Test script to debug router inclusion issue.
"""

import os
import sys
from pathlib import Path

# Set up environment variables before importing anything
os.environ.update({
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'SQUARE_APPLICATION_ID': 'test',
    'SQUARE_ACCESS_TOKEN': 'test',
    'TWILIO_ACCOUNT_SID': 'test',
    'TWILIO_AUTH_TOKEN': 'test',
    'TWILIO_PHONE_NUMBER': 'test',
    'ELEVENLABS_API_KEY': 'test',
    'SMTP_USERNAME': 'test',
    'SMTP_PASSWORD': 'test',
    'MANAGER_EMAIL': 'test@test.com',
    'SALON_PHONE': 'test',
    'SALON_ADDRESS': 'test',
    'SECRET_KEY': 'test',
    'ENCRYPTION_KEY': 'test' * 8  # 32 characters
})

# Temporarily move .env file
env_file = Path('.env')
env_backup = Path('.env.router_test_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    print("🔍 Testing router inclusion...")
    
    from fastapi import APIRouter
    
    # Create test routers
    main_router = APIRouter()
    sub_router = APIRouter(prefix="/test", tags=["test"])
    
    @sub_router.get("/hello")
    def test_endpoint():
        return {"message": "hello"}
    
    print(f"Before inclusion: main_router has {len(main_router.routes)} routes")
    print(f"Before inclusion: sub_router has {len(sub_router.routes)} routes")
    
    # Include sub-router
    main_router.include_router(sub_router)
    
    print(f"After inclusion: main_router has {len(main_router.routes)} routes")
    
    # Now test the actual routers
    print("\n🔍 Testing actual routers...")
    
    from api.routes import api_router, webhooks_router, admin_router, twiml_router
    
    print(f"api_router routes before manual inclusion: {len(api_router.routes)}")
    print(f"webhooks_router routes: {len(webhooks_router.routes)}")
    print(f"admin_router routes: {len(admin_router.routes)}")
    print(f"twiml_router routes: {len(twiml_router.routes)}")
    
    # Try manual inclusion
    new_router = APIRouter()
    new_router.include_router(webhooks_router)
    new_router.include_router(admin_router)
    new_router.include_router(twiml_router)
    
    print(f"new_router after manual inclusion: {len(new_router.routes)} routes")
    
    for route in new_router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"   Route: {route.methods} {route.path}")
    
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)
