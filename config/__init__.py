"""
Configuration Package
Handles all configuration settings for the Twitter bot.
"""

from .settings import get_api_credentials, get_bot_config
from .github_settings import get_github_config

__all__ = ['get_api_credentials', 'get_bot_config', 'get_github_config']
