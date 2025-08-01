# Setup and Utility Scripts

This directory contains setup scripts and utilities for the TwistyVoice AI promotional calling system.

## Scripts

### Setup and Installation
- `setup.py` - Main setup script for project initialization and dependency management

## Usage

### Initial Project Setup
```bash
# Run the setup script
python scripts/setup.py
```

This script typically handles:
- Virtual environment creation
- Dependency installation
- Database initialization
- Configuration file setup
- Initial data seeding

## Development Workflow

These scripts are designed to streamline the development setup process:

1. **First-time Setup**: Run setup scripts to get the environment ready
2. **Environment Validation**: Verify all dependencies and configurations
3. **Database Preparation**: Initialize and migrate database schemas
4. **Service Validation**: Test connections to external services

## Prerequisites

Before running setup scripts:
- Python 3.8+ installed
- Git repository cloned
- Required system dependencies available

## Note

Setup scripts may modify your local environment, create virtual environments, and install packages. Review the scripts before running them in production or sensitive environments.