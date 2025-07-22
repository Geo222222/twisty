# TwistyVoice Quick Start Guide

Get TwistyVoice AI Assistant up and running in minutes!

## 🚀 Quick Setup (Development)

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (minimum required):
# - SQUARE_APPLICATION_ID
# - SQUARE_ACCESS_TOKEN  
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER
# - SMTP_USERNAME
# - SMTP_PASSWORD
# - MANAGER_EMAIL
# - SECRET_KEY
# - ENCRYPTION_KEY
```

### 3. Initialize Database

```bash
# Run setup script
python scripts/setup.py
```

### 4. Start the Application

```bash
# Run development server
python -m src.main
```

### 5. Test the System

Visit `http://localhost:8000/docs` to see the API documentation and test endpoints.

## 🐳 Docker Setup (Production)

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with production values
```

### 2. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec twistyvoice python scripts/setup.py

# Check logs
docker-compose logs -f twistyvoice
```

## 📞 API Key Setup Guide

### Square API Keys

1. Go to [Square Developer Dashboard](https://developer.squareup.com/)
2. Create a new application
3. Get your Application ID and Access Token
4. For production, switch to Production environment

### Twilio API Keys

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number for voice calls
4. Configure webhooks (see deployment guide)

### ElevenLabs (Optional - for better TTS)

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Get your API key from settings
3. Choose a voice ID from your available voices

## 🧪 Testing the System

### 1. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get customers
curl http://localhost:8000/api/v1/admin/customers

# Get promotions
curl http://localhost:8000/api/v1/admin/promotions
```

### 2. Test Voice Calls (Development)

```bash
# Make a test call (requires customer and promotion IDs)
curl -X POST "http://localhost:8000/api/v1/admin/test/call?customer_id=1&promotion_id=1"
```

### 3. Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_promotion_engine.py -v
```

## 📊 Using the System

### 1. Customer Management

- Customers are automatically synced from Square
- View customer details and conversation history via API
- Customer segmentation happens automatically

### 2. Promotion Campaigns

- Promotions are loaded from `data/sample_promotions.yaml`
- The system automatically selects the best promotion for each customer
- Campaigns run on scheduled intervals

### 3. Call Scheduling

- Promotional calls run automatically (weekdays 10 AM and 2 PM)
- Appointment reminders sent 24 hours before appointments
- Follow-up calls scheduled based on customer responses

### 4. Reports

- Daily reports sent every morning at 8 AM
- Weekly reports sent Monday at 9 AM
- View analytics via API endpoints

## 🔧 Configuration Options

### Call Campaign Settings

```bash
# In .env file
MAX_CALLS_PER_DAY=50          # Limit daily calls
CALL_RETRY_ATTEMPTS=2         # Retry failed calls
RESPECT_DND_HOURS=true        # Honor do-not-disturb hours
DND_START_HOUR=20             # 8 PM
DND_END_HOUR=9                # 9 AM
```

### Business Settings

```bash
SALON_NAME=GetTwisted Hair Studios
SALON_PHONE=+1234567890
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00
TIMEZONE=America/New_York
```

### Compliance Settings

```bash
TCPA_COMPLIANCE=true
AUTO_OPT_OUT_KEYWORDS=STOP,UNSUBSCRIBE,REMOVE,QUIT
DATA_RETENTION_DAYS=365
```

## 📱 Webhook Configuration

For production, configure these Twilio webhooks:

1. **Voice Status Webhook:**
   - URL: `https://yourdomain.com/api/v1/webhooks/call_status`
   - Method: POST

2. **SMS Webhook:**
   - URL: `https://yourdomain.com/api/v1/webhooks/incoming_sms`
   - Method: POST

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error:**
   ```bash
   # Check if database file exists
   ls -la twistyvoice.db
   
   # Recreate database
   python scripts/setup.py
   ```

2. **Twilio Authentication Error:**
   ```bash
   # Verify credentials in .env
   echo $TWILIO_ACCOUNT_SID
   echo $TWILIO_AUTH_TOKEN
   ```

3. **Square API Error:**
   ```bash
   # Check environment setting
   echo $SQUARE_ENVIRONMENT  # should be 'sandbox' for testing
   ```

4. **Import Errors:**
   ```bash
   # Make sure you're in the right directory
   cd twisty
   
   # Check Python path
   export PYTHONPATH=$PWD/src:$PYTHONPATH
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📚 Next Steps

1. **Customize Promotions:** Edit `data/sample_promotions.yaml`
2. **Configure Voice Messages:** Modify voice templates in promotion engine
3. **Set Up Monitoring:** Configure log aggregation and alerts
4. **Scale for Production:** See `docs/DEPLOYMENT.md`

## 🆘 Getting Help

- **Documentation:** Check `docs/` directory
- **API Reference:** Visit `/docs` endpoint when running
- **Logs:** Check `logs/twistyvoice.log` for detailed information
- **Issues:** Review error messages and check configuration

## 🎯 Key Features to Test

1. **Automatic Customer Segmentation:** Check how customers are categorized
2. **Promotion Matching:** Verify appropriate promotions are selected
3. **Call Scheduling:** Confirm calls respect business hours and DND settings
4. **Booking Integration:** Test appointment creation flow
5. **Reporting:** Verify daily/weekly reports are generated

Happy calling! 📞✨
