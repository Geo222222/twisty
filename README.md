# TwistyVoice AI Assistant

🌟 **An autonomous AI-driven assistant system for GetTwisted Hair Studios**

## Overview

TwistyVoice is a modular system that autonomously:
- Calls and texts clients about specials, promotions, and availability
- Books appointments directly into the Square Appointment system
- Reports activities and outcomes to salon managers
- Logs client preferences and engagement history for future targeting

## Architecture

### Core Modules

| Module | Role |
|--------|------|
| `SquareConnector` | Authenticates and fetches customer + booking data |
| `PromotionEngine` | Chooses which offers/specials to promote |
| `VoiceAgent` | Calls/texts customers using Twilio |
| `BookingHandler` | Books appointments in Square via API |
| `ConversationTracker` | Logs call outcomes and client responses |
| `ReportGenerator` | Sends daily/weekly reports to the manager |
| `Scheduler` | Triggers call sessions (cron or time-based logic) |
| `Dashboard` | Optional visual admin panel |

### Technology Stack

- **Backend**: Python (FastAPI)
- **Telephony**: Twilio (Programmable Voice + SMS)
- **TTS/Voice AI**: ElevenLabs, Google TTS, or OpenAI
- **Data Store**: SQLite (local) or PostgreSQL (prod)
- **Scheduling**: APScheduler
- **Reporting**: Email + CSV + Web UI
- **Deployment**: Docker + GitHub Actions + Railway/Render

## Project Structure

```
twisty/
├── src/
│   ├── core/                    # Core business logic
│   │   ├── square_connector.py
│   │   ├── promotion_engine.py
│   │   ├── voice_agent.py
│   │   ├── booking_handler.py
│   │   ├── conversation_tracker.py
│   │   ├── report_generator.py
│   │   └── scheduler.py
│   ├── models/                  # Data models
│   ├── api/                     # FastAPI routes
│   ├── utils/                   # Utility functions
│   └── config/                  # Configuration management
├── tests/                       # Test suite
├── data/                        # Data files (promotions, templates)
├── logs/                        # Application logs
├── docker/                      # Docker configuration
├── scripts/                     # Deployment and utility scripts
└── docs/                        # Documentation
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Development Server**
   ```bash
   python -m src.main
   ```

## Security & Compliance

- ✅ TCPA compliance for marketing calls/texts
- ✅ Opt-out (Do Not Call) list management
- ✅ Secure credential handling
- ✅ HTTPS and token-based authentication
- ✅ Minimal data retention policy

## Development Roadmap

### Week 1: Foundation
- [x] Project setup and architecture
- [ ] SquareConnector + mock data
- [ ] Promotion YAML configuration

### Week 2: Voice Integration
- [ ] VoiceAgent call demo (TTS + response logger)
- [ ] Twilio integration

### Week 3: Booking System
- [ ] BookingHandler end-to-end with Square
- [ ] Appointment availability checking

### Week 4: Automation
- [ ] Promotion Campaign Scheduler
- [ ] Automated call triggers

### Week 5: Reporting
- [ ] Manager Report System
- [ ] Email notifications

### Week 6: Production
- [ ] Production deployment
- [ ] Web Dashboard (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Private - GetTwisted Hair Studios
