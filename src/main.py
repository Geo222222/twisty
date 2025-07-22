"""
TwistyVoice AI Assistant - Main Application Entry Point

This module initializes and runs the TwistyVoice FastAPI application.
"""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent))

from config.settings import get_settings
from api.routes import api_router
from core.scheduler import TwistyScheduler
from utils.logging_config import setup_logging

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-driven assistant system for GetTwisted Hair Studios",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://gettwistedhair.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Global scheduler instance
scheduler = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global scheduler
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize scheduler
    scheduler = TwistyScheduler()
    await scheduler.start()
    
    logger.info("TwistyVoice AI Assistant started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    global scheduler
    
    logger.info("Shutting down TwistyVoice AI Assistant")
    
    if scheduler:
        await scheduler.stop()
    
    logger.info("Shutdown complete")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


def main():
    """Main entry point for running the application."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
