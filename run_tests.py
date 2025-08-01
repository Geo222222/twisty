#!/usr/bin/env python3
"""
Test runner script that sets up the environment properly for running tests.
"""

import os
import sys
import subprocess

# Set up environment variables for testing
test_env = os.environ.copy()
test_env.update({
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
    'ENCRYPTION_KEY': 'test' * 8  # 32 characters
})

# Temporarily rename .env file to avoid conflicts
env_file = '.env'
env_backup = '.env.test_backup'

if os.path.exists(env_file):
    os.rename(env_file, env_backup)

try:
    # Run the tests
    if len(sys.argv) > 1:
        # Run specific test file or pytest arguments
        cmd = [sys.executable, '-m', 'pytest'] + sys.argv[1:]
    else:
        # Run all tests in the tests directory
        cmd = [sys.executable, '-m', 'pytest', 'tests/', '-v']

    result = subprocess.run(cmd, env=test_env)
    sys.exit(result.returncode)

finally:
    # Restore .env file
    if os.path.exists(env_backup):
        os.rename(env_backup, env_file)
