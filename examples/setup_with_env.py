#!/usr/bin/env python3
"""
Setup script that properly handles environment variables.
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
env_backup = Path('.env.setup_backup')

if env_file.exists():
    env_file.rename(env_backup)

try:
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    # Now import and run setup
    from scripts.setup import main
    
    print("🚀 Running TwistyVoice setup with proper environment...")
    main()
    print("✅ Setup completed successfully!")
    
finally:
    # Restore .env file
    if env_backup.exists():
        env_backup.rename(env_file)
