#!/usr/bin/env python3
"""
Production Twitter Bot V2 - Optimized for Twitter API v2
Multi-layered sentiment analysis with intelligent posting
"""

import os
import time
import json
import tweepy
from datetime import datetime, timedelta
from bot.sentiment_analyzer import SentimentAnalyzer
from bot.analytics import AnalyticsTracker
from config.settings import load_config, get_api_credentials
from utils.logger import get_logger

class ProductionBotV2:
    def __init__(self):
        self.logger = get_logger("production_bot_v2")
        self.config = load_config()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.analytics = AnalyticsTracker()
        self.client = self._initialize_twitter_api_v2()
        self.monthly_limit = 500
        self.daily_limit = 16  # Conservative: 500/31 days
        
    def _initialize_twitter_api_v2(self):
        """Initialize Twitter API v2 Client"""
        try:
            credentials = get_api_credentials()
            
            client = tweepy.Client(
                consumer_key=credentials['consumer_key'],
                consumer_secret=credentials['consumer_secret'],
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_token_secret']
            )
            
            # Test authentication
            me = client.get_me()
            self.logger.info(f"API v2 authentication successful for @{me.data.username}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API v2: {e}")
            return None
    
    def _check_posting_limits(self):
        """Check if we can post within daily/monthly limits"""
        today = datetime.now().date()
        daily_stats = self.analytics.get_daily_stats(today.isoformat())
        
        daily_tweets = daily_stats.get('tweets_posted', 0)
        
        if daily_tweets >= self.daily_limit:
            self.logger.warning(f"Daily limit reached: {daily_tweets}/{self.daily_limit}")
            return False
            
        return True
    
    def post_intelligent_tweet(self, content, force=False):
        """Post tweet with sentiment analysis and API v2"""
        if not self.client:
            self.logger.error("Twitter API v2 not initialized")
            return False
            
        if not force and not self._check_posting_limits():
            self.logger.info("Posting limits reached, skipping tweet")
            return False
        
        # Analyze sentiment first
        sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
        
        # Only post if sentiment is positive or high-confidence neutral
        if sentiment_result['sentiment'] == 'negative' and sentiment_result['confidence'] > 0.5:
            self.logger.info(f"Skipping negative sentiment tweet")
            return False
        
        try:
            # Post with API v2
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            
            # Record analytics
            self.analytics.record_tweet(
                tweet_id, 
                content, 
                tweet_type='intelligent_v2'
            )
            
            self.logger.info(f"Tweet posted successfully: {tweet_id}")
            print(f"SUCCESS! Tweet posted:")
            print(f"  Content: {content}")
            print(f"  Tweet ID: {tweet_id}")
            print(f"  Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']:.3f})")
            print(f"  URL: https://twitter.com/dishanaa11/status/{tweet_id}")
            
            return True
            
        except tweepy.TooManyRequests:
            self.logger.error("Rate limit exceeded")
            return False
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return False
    
    def schedule_and_post_content(self, content_list):
        """Process and post a list of content with intelligent timing"""
        print("\nINTELLIGENT CONTENT PROCESSING")
        print("=" * 50)
        
        posted_count = 0
        for i, content in enumerate(content_list):
            print(f"\nProcessing content {i+1}/{len(content_list)}:")
            print(f"Content: {content[:80]}{'...' if len(content) > 80 else ''}")
            
            # Analyze sentiment
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
            print(f"Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']:.3f})")
            
            # Decide whether to post
            should_post = (
                sentiment_result['sentiment'] == 'positive' or 
                (sentiment_result['sentiment'] == 'neutral' and sentiment_result['confidence'] < 0.3)
            )
            
            if should_post and self._check_posting_limits():
                print("Posting now...")
                success = self.post_intelligent_tweet(content)
                if success:
                    posted_count += 1
                    # Wait between posts to avoid rate limits
                    if i < len(content_list) - 1:
                        print("Waiting 30 seconds before next post...")
                        time.sleep(30)
                else:
                    print("Failed to post")
            else:
                reason = "negative sentiment" if sentiment_result['sentiment'] == 'negative' else "daily limit reached"
                print(f"Skipped: {reason}")
        
        print(f"\nPosting summary: {posted_count}/{len(content_list)} tweets posted")
        return posted_count
    
    def demonstrate_capabilities(self):
        """Demonstrate bot capabilities with real posting"""
        print("PRODUCTION TWITTER BOT V2 - LIVE DEMONSTRATION")
        print("=" * 60)
        
        if not self.client:
            print("Twitter API v2 not available")
            return
            
        # Show current limits
        today = datetime.now().date()
        daily_stats = self.analytics.get_daily_stats(today.isoformat())
        daily_tweets = daily_stats.get('tweets_posted', 0)
        remaining = max(0, self.daily_limit - daily_tweets)
        
        print(f"Daily posting status: {daily_tweets}/{self.daily_limit} used, {remaining} remaining")
        
        # Sample content optimized for positive sentiment
        demo_content = [
            f"Excited to share my Python Twitter automation bot! Multi-layered sentiment analysis with VADER and TextBlob working perfectly! #{datetime.now().strftime('%m%d')} #Python #AI #automation",
            f"Amazing results from my intelligent Twitter bot! The sentiment analysis ensures only positive content gets posted. Love this project! #TwitterBot #Python",
            f"Building the future of social media automation! My bot analyzes sentiment before posting - smart, efficient, and effective! #innovation #tech"
        ]
        
        print(f"\nDemo content prepared: {len(demo_content)} tweets")
        print("Each will be analyzed for sentiment before posting")
        
        # Process and post content
        posted = self.schedule_and_post_content(demo_content)
        
        print(f"\nDemonstration complete!")
        print(f"Posted: {posted} tweets")
        print(f"Remaining daily posts: {max(0, remaining - posted)}")
        
        # Show final analytics
        final_stats = self.analytics.get_daily_stats(today.isoformat())
        print(f"Total tweets today: {final_stats.get('tweets_posted', 0)}")

if __name__ == "__main__":
    bot = ProductionBotV2()
    bot.demonstrate_capabilities()
