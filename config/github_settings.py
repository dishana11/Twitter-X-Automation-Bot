"""
GitHub-compatible settings for environment variables
"""

import os
import json
import logging

def get_api_credentials():
    """Get Twitter API credentials from environment variables (GitHub secrets compatible)"""
    return {
        'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
        'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
        'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
    }

def load_config(config_path='config/config.json'):
    """Load configuration with fallback defaults for GitHub deployment"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Default configuration for GitHub deployments
        config = {
            "bot": {
                "name": "Twitter Automation Bot",
                "max_daily_replies": 50,
                "reply_keywords": ["AI", "automation", "python", "bot"],
                "post_interval_hours": 24
            },
            "hashtags": {
                "monitor": ["#AI", "#Technology", "#Innovation", "#Python", "#Automation"],
                "use_in_posts": True,
                "max_per_tweet": 3
            },
            "sentiment": {
                "positive_threshold": 0.1,
                "negative_threshold": -0.1,
                "confidence_threshold": 0.5
            },
            "limits": {
                "daily_tweets": 16,
                "monthly_tweets": 500,
                "rate_limit_window": 15
            }
        }
    return config

def validate_config(config):
    """Validate configuration structure"""
    required_sections = ['bot', 'hashtags', 'sentiment', 'limits']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    return True

def create_default_config(config_path):
    """Create default configuration file"""
    default_config = {
        "bot": {
            "name": "Twitter Automation Bot",
            "max_daily_replies": 50,
            "reply_keywords": ["AI", "automation", "python", "bot"],
            "post_interval_hours": 24
        },
        "hashtags": {
            "monitor": ["#AI", "#Technology", "#Innovation", "#Python", "#Automation"],
            "use_in_posts": True,
            "max_per_tweet": 3
        },
        "sentiment": {
            "positive_threshold": 0.1,
            "negative_threshold": -0.1,
            "confidence_threshold": 0.5
        },
        "limits": {
            "daily_tweets": 16,
            "monthly_tweets": 500,
            "rate_limit_window": 15
        }
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    return default_config

def get_github_config():
    """Alias for loading the GitHub config, for compatibility."""
    return load_config()
