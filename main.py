import asyncio
from uvicorn import run
from config import Config
from src.presentation.telegram.webhook import app


def main():
    """Main entry point for the application"""
    print("Starting Telegram Bot Webhook Server...")
    print(f"Server will run on {Config.HOST}:{Config.PORT}")
    
    # Run the FastAPI application with uvicorn
    run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG  # Enable auto-reload in debug mode
    )


if __name__ == "__main__":
    main()