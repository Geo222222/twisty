# Examples and Demo Scripts

This directory contains example scripts and demonstrations of the TwistyVoice AI promotional calling system functionality.

## Scripts Overview

### Promotional Campaigns
- `add_back_to_school_promo.py` - Adds back-to-school promotional campaign data
- `send_promo_text.py` - Sends promotional text messages to customers
- `resend_promo_text.py` - Resends promotional texts to specific customers

### Direct Calling Examples
- `make_direct_call.py` - Example of making direct calls through the system
- `make_real_call.py` - Real call implementation example
- `call_dj_martin.py` - Specific example call to DJ Martin

### Setup and Data Management
- `setup_with_env.py` - Environment setup and configuration
- `seed_test_data.py` - Seeds the database with test customer data
- `run_main.py` - Alternative main application runner

## Usage

These scripts are primarily for:
- **Development and Testing**: Understanding how the system works
- **Data Setup**: Populating the system with test data
- **Campaign Examples**: Demonstrating promotional workflows

## Prerequisites

Before running any scripts, ensure:
1. The virtual environment is activated
2. All dependencies are installed (`pip install -r requirements.txt`)
3. Environment variables are properly configured (see `.env.example`)
4. The main application database is initialized

## Running Examples

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run a specific example
python examples/send_promo_text.py

# Or run with the module path
python -m examples.send_promo_text
```

## Note

⚠️ **Important**: These examples may make real API calls to Twilio, Square, or other services depending on your configuration. Review and modify the scripts as needed for your testing environment.