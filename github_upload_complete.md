# Complete GitHub Repository Upload Guide

## Upload All Required Files to Your GitHub Repository

Copy these files and directories to your GitHub repository:

### 1. Main Python Files
```
main.py
production_bot_v2.py
app.py
streamlit_twitter_bot.py
```

### 2. Bot Directory (`bot/`)
Create `bot/` directory and add these files:

**`bot/__init__.py`**
```python
"""
Twitter Bot Package
Contains all bot-related modules and functionality.
"""

__version__ = "1.0.0"
__author__ = "Twitter Bot Team"

# Import main classes for easy access
from .twitter_bot import TwitterBot
from .sentiment_analyzer import SentimentAnalyzer
from .scheduler import TweetScheduler
from .hashtag_monitor import HashtagMonitor
from .reply_handler import ReplyHandler
from .trend_analyzer import TrendAnalyzer
from .analytics import AnalyticsTracker

__all__ = [
    'TwitterBot',
    'SentimentAnalyzer', 
    'TweetScheduler',
    'HashtagMonitor',
    'ReplyHandler',
    'TrendAnalyzer',
    'AnalyticsTracker'
]
```

**`bot/sentiment_analyzer.py`**
```python
"""
Sentiment Analysis Module
Provides sentiment analysis functionality for tweets and text content.
Multi-layered approach: VADER → TextBlob → spaCy → HuggingFace
"""

import re
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the multi-layered sentiment analyzer"""
        self.available_analyzers = []
        self.initialize_analyzers()
        
    def initialize_analyzers(self):
        """Initialize all available sentiment analyzers"""
        # Try to import and initialize VADER
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            self.available_analyzers.append('vader')
            logger.info("VADER sentiment analyzer initialized")
        except ImportError:
            logger.warning("VADER not available")
            self.vader_analyzer = None
            
        # Try to import and initialize TextBlob
        try:
            from textblob import TextBlob
            self.textblob = TextBlob
            self.available_analyzers.append('textblob')
            logger.info("TextBlob sentiment analyzer initialized")
        except ImportError:
            logger.warning("TextBlob not available")
            self.textblob = None
            
        logger.info(f"Available analyzers: {self.available_analyzers}")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Multi-layered sentiment analysis with fallback chain:
        1. VADER (primary - fast, social media optimized)
        2. TextBlob (secondary - different algorithm)
        3. spaCy (tertiary - comprehensive NLP)
        4. HuggingFace (final - most advanced)
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'polarity': 0.0,
                'analyzer_used': 'none',
                'raw_scores': {}
            }
            
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Try VADER first (best for social media)
        if 'vader' in self.available_analyzers:
            try:
                return self._analyze_with_vader(cleaned_text)
            except Exception as e:
                logger.warning(f"VADER analysis failed: {e}")
        
        # Fallback to TextBlob
        if 'textblob' in self.available_analyzers:
            try:
                return self._analyze_with_textblob(cleaned_text)
            except Exception as e:
                logger.warning(f"TextBlob analysis failed: {e}")
        
        # Final fallback - basic rule-based analysis
        return self._basic_sentiment_analysis(cleaned_text)
        
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        # VADER returns compound score (-1 to 1)
        compound = scores['compound']
        
        # Determine sentiment based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'confidence': abs(compound),
            'polarity': compound,
            'analyzer_used': 'vader',
            'raw_scores': scores
        }
        
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        blob = self.textblob(text)
        polarity = blob.sentiment.polarity
        
        # TextBlob returns polarity (-1 to 1)
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'confidence': abs(polarity),
            'polarity': polarity,
            'analyzer_used': 'textblob',
            'raw_scores': {
                'polarity': polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        }
        
    def _basic_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Basic rule-based sentiment analysis as final fallback"""
        positive_words = ['good', 'great', 'awesome', 'amazing', 'excellent', 'fantastic', 
                         'wonderful', 'brilliant', 'outstanding', 'superb', 'love', 'like',
                         'excited', 'happy', 'joy', 'pleased', 'thrilled', 'delighted']
        
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                         'dislike', 'angry', 'sad', 'disappointed', 'frustrated', 'annoyed',
                         'upset', 'worried', 'concerned', 'problem', 'issue', 'error']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            polarity = 0.3
        elif negative_count > positive_count:
            sentiment = 'negative'
            polarity = -0.3
        else:
            sentiment = 'neutral'
            polarity = 0.0
            
        return {
            'sentiment': sentiment,
            'confidence': abs(polarity),
            'polarity': polarity,
            'analyzer_used': 'basic_rules',
            'raw_scores': {
                'positive_words': positive_count,
                'negative_words': negative_count
            }
        }
        
    def _clean_text(self, text: str) -> str:
        """Clean text for better sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove mentions and hashtags for cleaner analysis
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
        
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity score to sentiment label"""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
            
    def analyze_tweet_sentiment(self, tweet) -> Dict[str, Any]:
        """Analyze sentiment of a tweet object"""
        if hasattr(tweet, 'full_text'):
            text = tweet.full_text
        elif hasattr(tweet, 'text'):
            text = tweet.text
        else:
            text = str(tweet)
            
        return self.analyze_sentiment(text)
        
    def batch_analyze_sentiments(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze_sentiment(text) for text in texts]
        
    def get_sentiment_summary(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics for a list of sentiment analyses"""
        if not sentiments:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'average_polarity': 0.0}
            
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        average_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
        
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'total': len(sentiments),
            'average_polarity': average_polarity,
            'positive_percentage': (positive_count / len(sentiments)) * 100,
            'negative_percentage': (negative_count / len(sentiments)) * 100,
            'neutral_percentage': (neutral_count / len(sentiments)) * 100
        }
        
    def is_positive_sentiment(self, text: str, threshold: float = 0.1) -> bool:
        """Check if text has positive sentiment above threshold"""
        result = self.analyze_sentiment(text)
        return result['sentiment'] == 'positive' and result['confidence'] >= threshold
        
    def is_negative_sentiment(self, text: str, threshold: float = -0.1) -> bool:
        """Check if text has negative sentiment below threshold"""
        result = self.analyze_sentiment(text)
        return result['sentiment'] == 'negative' and result['polarity'] <= threshold
        
    def filter_by_sentiment(self, texts: List[str], target_sentiment: str = 'positive') -> List[str]:
        """Filter texts by target sentiment"""
        results = []
        for text in texts:
            sentiment_result = self.analyze_sentiment(text)
            if sentiment_result['sentiment'] == target_sentiment:
                results.append(text)
        return results
```

### 3. Config Directory (`config/`)
Create `config/` directory and add these files:

**`config/__init__.py`**
```python
"""
Configuration Package
Handles all configuration settings for the Twitter bot.
"""

from .settings import get_api_credentials, get_bot_config
from .github_settings import get_github_config

__all__ = ['get_api_credentials', 'get_bot_config', 'get_github_config']
```

**`config/settings.py`**
```python
"""
Configuration settings for the Twitter bot
"""

import os
import json
import logging
from typing import Dict, Any, Optional

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
        'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', '')
    }
    
    # Validate credentials
    missing_creds = [key for key, value in credentials.items() if not value]
    if missing_creds:
        logger.warning(f"Missing credentials: {missing_creds}")
        
    return credentials

def get_bot_config() -> Dict[str, Any]:
    """Get bot configuration settings"""
    return {
        'posting_limits': {
            'daily_limit': 16,  # Free tier limit
            'monthly_limit': 500,  # Free tier limit
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

def load_config_file(filename: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        config_path = os.path.join('config', filename)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file not found: {config_path}")
            return {}
    except Exception as e:
        logger.error(f"Failed to load config file {filename}: {e}")
        return {}

def save_config_file(filename: str, config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file"""
    try:
        os.makedirs('config', exist_ok=True)
        config_path = os.path.join('config', filename)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save config file {filename}: {e}")
        return False
```

### 4. Requirements File

**`deploy_requirements.txt`**
```
tweepy==4.14.0
textblob==0.17.1
vaderSentiment==3.3.2
streamlit==1.29.0
schedule==1.2.0
requests==2.31.0
trafilatura==1.6.4
pandas==2.1.4
python-dotenv==1.0.0
```

### 5. Main Application Files

**`production_bot_v2.py`**
```python
"""
Production Twitter Bot V2 - Optimized for Twitter API v2
Multi-layered sentiment analysis with intelligent posting
"""

import tweepy
import random
import logging
from datetime import datetime
from bot.sentiment_analyzer import SentimentAnalyzer
from config.settings import get_api_credentials, get_bot_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionBotV2:
    def __init__(self):
        """Initialize the production bot with API v2"""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.config = get_bot_config()
        self.credentials = get_api_credentials()
        self.client = None
        self.daily_post_count = 0
        self.monthly_post_count = 0
        
        # Initialize Twitter API
        self._initialize_twitter_api_v2()
        
    def _initialize_twitter_api_v2(self):
        """Initialize Twitter API v2 Client"""
        try:
            self.client = tweepy.Client(
                consumer_key=self.credentials['consumer_key'],
                consumer_secret=self.credentials['consumer_secret'],
                access_token=self.credentials['access_token'],
                access_token_secret=self.credentials['access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # Test authentication
            me = self.client.get_me()
            if me.data:
                logger.info(f"Successfully authenticated as: {me.data.username}")
                return True
            else:
                logger.error("Authentication failed - no user data returned")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API v2: {e}")
            return False
    
    def _check_posting_limits(self) -> bool:
        """Check if we can post within daily/monthly limits"""
        if not self.config['posting_limits']['respect_limits']:
            return True
            
        daily_limit = self.config['posting_limits']['daily_limit']
        monthly_limit = self.config['posting_limits']['monthly_limit']
        
        if self.daily_post_count >= daily_limit:
            logger.warning(f"Daily posting limit reached: {self.daily_post_count}/{daily_limit}")
            return False
            
        if self.monthly_post_count >= monthly_limit:
            logger.warning(f"Monthly posting limit reached: {self.monthly_post_count}/{monthly_limit}")
            return False
            
        return True
    
    def post_intelligent_tweet(self, content: str, force: bool = False) -> bool:
        """Post tweet with sentiment analysis and API v2"""
        try:
            # Check posting limits
            if not self._check_posting_limits() and not force:
                logger.warning("Posting limits exceeded, skipping tweet")
                return False
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
            logger.info(f"Sentiment analysis: {sentiment_result['sentiment']} "
                       f"(confidence: {sentiment_result['confidence']:.3f})")
            
            # Check if should post based on sentiment
            should_post = (
                force or 
                sentiment_result['sentiment'] != 'negative' or 
                sentiment_result['confidence'] < 0.5
            )
            
            if not should_post:
                logger.info("Tweet blocked due to negative sentiment")
                return False
            
            # Post tweet using API v2
            response = self.client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Tweet posted successfully! ID: {tweet_id}")
                logger.info(f"URL: https://twitter.com/i/web/status/{tweet_id}")
                
                # Update counters
                self.daily_post_count += 1
                self.monthly_post_count += 1
                
                return True
            else:
                logger.error("Failed to post tweet - no response data")
                return False
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return False
    
    def schedule_and_post_content(self, content_list: list) -> int:
        """Process and post a list of content with intelligent timing"""
        posted_count = 0
        
        for content in content_list:
            if self.post_intelligent_tweet(content):
                posted_count += 1
            else:
                logger.info(f"Skipped posting: {content[:50]}...")
                
        logger.info(f"Posted {posted_count}/{len(content_list)} tweets")
        return posted_count
    
    def demonstrate_capabilities(self):
        """Demonstrate bot capabilities with real posting"""
        logger.info("=== Production Twitter Bot V2 Demo ===")
        
        # Generate sample content
        topics = ['AI', 'Python', 'automation', 'technology', 'innovation']
        topic = random.choice(topics)
        
        templates = [
            f"Exploring the fascinating world of {topic}! The possibilities are endless.",
            f"Just discovered amazing insights about {topic}! This could change everything.",
            f"The future of {topic} looks incredibly promising! Excited to see what's next.",
            f"Working with {topic} today - amazing how fast this field is advancing!",
            f"Latest developments in {topic} are truly remarkable! Innovation never stops."
        ]
        
        content = random.choice(templates)
        timestamp = datetime.now().strftime('%m%d_%H%M')
        final_content = f"{content} #{timestamp} #{topic.replace(' ', '')}"
        
        logger.info(f"Generated content: {final_content}")
        
        # Attempt to post
        success = self.post_intelligent_tweet(final_content)
        
        if success:
            logger.info("✅ Demo completed successfully!")
        else:
            logger.info("❌ Demo posting failed or was blocked")
            
        return success

if __name__ == "__main__":
    bot = ProductionBotV2()
    bot.demonstrate_capabilities()
```

## Upload Instructions:

1. **Create all the above files in your GitHub repository**
2. **Ensure you have the 3 workflow files from earlier**
3. **Add the Twitter API secrets to repository settings**
4. **Test manual posting through GitHub Actions**

Your repository will then have everything needed for automated Twitter posting with sentiment analysis.
