
"""
Twitter Bot Module
Main bot functionality for posting and automation
"""

import tweepy
import logging
from datetime import datetime
from .sentiment_analyzer import SentimentAnalyzer
from config.settings import get_api_credentials, get_bot_config

logger = logging.getLogger(__name__)

class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot with API credentials and sentiment analyzer"""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.config = get_bot_config()
        self.credentials = get_api_credentials()
        self.client = self._initialize_twitter_api()
        
    def _initialize_twitter_api(self):
        """Initialize Twitter API v2 Client"""
        try:
            client = tweepy.Client(
                consumer_key=self.credentials['consumer_key'],
                consumer_secret=self.credentials['consumer_secret'],
                access_token=self.credentials['access_token'],
                access_token_secret=self.credentials['access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # Test authentication
            me = client.get_me()
            if me.data:
                logger.info(f"Successfully authenticated as: @{me.data.username}")
                return client
            else:
                logger.error("Authentication failed - no user data returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            return None
    
    def post_tweet(self, content, force_post=False):
        """
        Post a tweet with sentiment analysis
        
        Args:
            content (str): Tweet content
            force_post (bool): Skip sentiment check if True
            
        Returns:
            dict: Result with success status and tweet info
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Twitter API not initialized'
            }
        
        # Analyze sentiment unless forced
        if not force_post:
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
            
            # Block negative sentiment posts
            if (sentiment_result['sentiment'] == 'negative' and 
                sentiment_result['confidence'] > 0.5):
                return {
                    'success': False,
                    'error': 'Blocked due to negative sentiment',
                    'sentiment': sentiment_result
                }
        
        try:
            # Post the tweet
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            
            logger.info(f"Tweet posted successfully! ID: {tweet_id}")
            
            return {
                'success': True,
                'tweet_id': tweet_id,
                'url': f"https://twitter.com/i/web/status/{tweet_id}",
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_info(self):
        """Get authenticated user information"""
        if not self.client:
            return None
        
        try:
            me = self.client.get_me()
            return {
                'id': me.data.id,
                'username': me.data.username,
                'name': me.data.name
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
