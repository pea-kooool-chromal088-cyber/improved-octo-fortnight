import os
from typing import Optional


class Config:
    """Configuration class for the bot"""
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
    WEBHOOK_URL: Optional[str] = os.getenv('WEBHOOK_URL', 'https://your-domain.com/webhook')
    
    # Database settings
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'bot_database.db')
    
    # Server settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8000'))
    
    # Debug mode
    DEBUG: bool = bool(os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes'))