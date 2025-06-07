"""
Configuration settings for the Twitter bot
"""

import os
import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_api_credentials() -> Dict[str, str]:
    """Get Twitter API credentials from environment variables"""
    credentials = {
        'consumer_key': os.getenv('TWITTER_CONSUMER_KEY', ''),
        'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET', ''),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
        'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN', '')
    }
    missing_creds = [key for key, value in credentials.items() if not value]
    if missing_creds:
        logger.warning(f"Missing credentials: {missing_creds}")
    return credentials

def get_bot_config() -> Dict[str, Any]:
    """Get bot configuration settings"""
    return {
        'posting_limits': {
            'daily_limit': 16,
            'monthly_limit': 500,
            'respect_limits': True
        },
        'sentiment_analysis': {
            'enabled': True,
            'block_negative': True,
            'confidence_threshold': 0.1
        },
        'scheduling': {
            'enabled': True,
            'default_timezone': 'Asia/Kolkata',
            'daily_post_time': '10:00'
        },
        'monitoring': {
            'hashtag_monitoring': True,
            'auto_replies': True,
            'trend_analysis': True
        }
    }

def load_config(config_path='config/config.json'):
    """Load configuration with fallback defaults"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = get_bot_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        config = get_bot_config()
    return config
