# TwistyVoice Deployment Guide

This guide covers deploying TwistyVoice AI Assistant to production.

## Prerequisites

- Docker and Docker Compose
- Domain name with SSL certificate
- Twilio account with phone number
- Square developer account
- Email account for SMTP (Gmail recommended)

## Environment Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Required Variables

Edit `.env` with your production values:

```bash
# Application Settings
APP_NAME=TwistyVoice
DEBUG=false
LOG_LEVEL=INFO

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://twistyvoice:your_secure_password@db:5432/twistyvoice

# Square API (Production)
SQUARE_APPLICATION_ID=your_production_app_id
SQUARE_ACCESS_TOKEN=your_production_access_token
SQUARE_ENVIRONMENT=production

# Twilio (Production)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://yourdomain.com/api/v1

# Voice & TTS
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
MANAGER_EMAIL=manager@gettwistedhair.com

# Business Configuration
SALON_NAME=GetTwisted Hair Studios
SALON_PHONE=+1234567890
SALON_ADDRESS=123 Main St, City, State 12345
TIMEZONE=America/New_York

# Security
SECRET_KEY=your_32_character_secret_key_here
ENCRYPTION_KEY=your_32_character_encryption_key

# Production Settings
MOCK_CALLS=false
MOCK_SMS=false
TCPA_COMPLIANCE=true
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database:**
   ```bash
   docker-compose exec twistyvoice python scripts/setup.py
   ```

3. **Check logs:**
   ```bash
   docker-compose logs -f twistyvoice
   ```

### Option 2: Railway Deployment

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set environment variables:**
   ```bash
   railway variables set DATABASE_URL=postgresql://...
   railway variables set TWILIO_ACCOUNT_SID=...
   # ... set all required variables
   ```

### Option 3: Render Deployment

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: twistyvoice
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python -m src.main
       envVars:
         - key: DATABASE_URL
           fromDatabase:
             name: twistyvoice-db
             property: connectionString
   
   databases:
     - name: twistyvoice-db
       databaseName: twistyvoice
       user: twistyvoice
   ```

2. **Connect GitHub repository to Render**

3. **Set environment variables in Render dashboard**

## SSL/HTTPS Configuration

### Using Let's Encrypt with Nginx

1. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Update nginx configuration:**
   ```nginx
   server {
       listen 443 ssl;
       server_name yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://twistyvoice:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Twilio Webhook Configuration

1. **Configure Voice Webhook:**
   - URL: `https://yourdomain.com/api/v1/webhooks/call_status`
   - HTTP Method: POST

2. **Configure SMS Webhook:**
   - URL: `https://yourdomain.com/api/v1/webhooks/incoming_sms`
   - HTTP Method: POST

## Monitoring and Logging

### 1. Application Logs

```bash
# View real-time logs
docker-compose logs -f twistyvoice

# View specific service logs
docker-compose logs db
docker-compose logs redis
```

### 2. Health Checks

- Application health: `https://yourdomain.com/health`
- API documentation: `https://yourdomain.com/docs`

### 3. Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U twistyvoice -d twistyvoice

# Check table sizes
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size 
FROM pg_tables WHERE schemaname='public';
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U twistyvoice twistyvoice > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U twistyvoice twistyvoice < backup_20240101.sql
```

### 2. Application Data Backup

```bash
# Backup logs and data
tar -czf twistyvoice_backup_$(date +%Y%m%d).tar.gz logs/ data/
```

## Security Considerations

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 3. Secret Management

- Use environment variables for all secrets
- Rotate API keys regularly
- Monitor access logs

## Scaling Considerations

### 1. Horizontal Scaling

```yaml
# docker-compose.yml
services:
  twistyvoice:
    deploy:
      replicas: 3
    # ... other configuration
```

### 2. Database Optimization

- Enable connection pooling
- Add database indexes for frequently queried fields
- Consider read replicas for reporting

### 3. Caching

- Use Redis for session storage
- Cache frequently accessed data
- Implement API response caching

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   ```bash
   # Check database status
   docker-compose exec db pg_isready -U twistyvoice
   ```

2. **Twilio Webhook Failures:**
   - Verify webhook URLs are accessible
   - Check SSL certificate validity
   - Review Twilio debugger logs

3. **High Memory Usage:**
   ```bash
   # Monitor container resources
   docker stats
   ```

### Performance Optimization

1. **Database Query Optimization:**
   - Add indexes for frequently queried columns
   - Use database query profiling

2. **Application Performance:**
   - Enable async processing for long-running tasks
   - Implement request rate limiting

3. **Resource Monitoring:**
   - Set up alerts for high CPU/memory usage
   - Monitor disk space usage

## Maintenance Schedule

### Daily
- Check application logs for errors
- Monitor system resources
- Verify scheduled tasks are running

### Weekly
- Review call analytics and reports
- Update promotion campaigns
- Check database performance

### Monthly
- Update dependencies and security patches
- Rotate API keys and secrets
- Review and optimize database queries
- Backup and test restore procedures
