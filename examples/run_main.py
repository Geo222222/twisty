#!/usr/bin/env python3
"""
Run the main TwistyVoice application with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set up environment variables before importing anything
os.environ.update({
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'SQUARE_APPLICATION_ID': 'test',
    'SQUARE_ACCESS_TOKEN': 'test',
    'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID', 'test'),
    'TWILIO_AUTH_TOKEN': os.getenv('TWILIO_AUTH_TOKEN', 'test'),
    'TWILIO_PHONE_NUMBER': os.getenv('TWILIO_PHONE_NUMBER', 'test'),
    'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY', 'test'),
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
env_backup = Path('.env.main_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    print("🚀 Starting TwistyVoice main application...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🔧 Debug mode enabled")
    print()
    
    # Run the main application
    result = subprocess.run([
        sys.executable, '-m', 'src.main'
    ], cwd=Path.cwd())
    
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)
