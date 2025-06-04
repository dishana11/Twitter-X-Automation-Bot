#!/usr/bin/env python3
"""
Streamlit Twitter Bot Interface
Interactive dashboard for manual posting, scheduled tweets, and trend-based content generation
"""

import streamlit as st
import tweepy
import time
import schedule
import threading
import requests
from datetime import datetime, timezone, timedelta
import json
import pytz
from bot.sentiment_analyzer import SentimentAnalyzer
from bot.analytics import AnalyticsTracker
from config.settings import get_api_credentials
from utils.logger import get_logger

class StreamlitTwitterBot:
    def __init__(self):
        self.logger = get_logger("streamlit_bot")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.analytics = AnalyticsTracker()
        self.client = self._initialize_api()
        
    def _initialize_api(self):
        """Initialize Twitter API v2"""
        try:
            credentials = get_api_credentials()
            client = tweepy.Client(
                consumer_key=credentials['consumer_key'],
                consumer_secret=credentials['consumer_secret'],
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_token_secret']
            )
            return client
        except Exception as e:
            st.error(f"Failed to initialize Twitter API: {e}")
            return None
    
    def search_topic_content(self, topic):
        """Search and generate content ideas based on topic"""
        content_ideas = []
        
        # Generate topic-based content variations
        base_templates = [
            f"Exploring the fascinating world of {topic}! The possibilities are endless and exciting! #innovation #technology",
            f"Just discovered amazing insights about {topic}! This could revolutionize how we think about the future! #trending #insights",
            f"Breaking: New developments in {topic} are reshaping our understanding! Incredible progress happening right now! #breakthrough",
            f"The future of {topic} looks incredibly promising! Excited to see where this technology takes us next! #future #tech",
            f"Deep dive into {topic} reveals some truly remarkable innovations! The potential applications are mind-blowing! #research #innovation"
        ]
        
        for i, template in enumerate(base_templates):
            # Analyze sentiment for each option
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(template)
            content_ideas.append({
                'id': chr(65 + i),  # A, B, C, D, E
                'content': template,
                'sentiment': sentiment_result['sentiment'],
                'confidence': sentiment_result['confidence'],
                'recommended': sentiment_result['sentiment'] == 'positive' and sentiment_result['confidence'] > 0.5
            })
        
        return content_ideas
    
    def get_trending_topics(self):
        """Get trending topics (simulated for demo - would use Twitter API trends in production)"""
        # Sample trending topics - in production, this would fetch real trends
        trending = [
            "Artificial Intelligence", "Machine Learning", "Python Programming",
            "Data Science", "Cloud Computing", "Cybersecurity",
            "Blockchain", "IoT", "5G Technology", "Quantum Computing"
        ]
        return trending
    
    def post_tweet(self, content):
        """Post tweet with sentiment analysis"""
        if not self.client:
            return False, "Twitter API not initialized"
        
        try:
            # Analyze sentiment first
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(content)
            
            if sentiment_result['sentiment'] == 'negative' and sentiment_result['confidence'] > 0.7:
                return False, f"Content has negative sentiment (confidence: {sentiment_result['confidence']:.2f}). Consider revising."
            
            # Post tweet
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            
            # Record analytics
            self.analytics.record_tweet(tweet_id, content, 'manual')
            
            return True, f"Tweet posted successfully! ID: {tweet_id}"
        
        except tweepy.Forbidden as e:
            if "duplicate" in str(e).lower():
                return False, "Duplicate content detected. Please modify your tweet."
            return False, f"Posting forbidden: {e}"
        except Exception as e:
            return False, f"Failed to post: {e}"

def setup_scheduler():
    """Setup scheduled posting at 10 AM IST"""
    ist = pytz.timezone('Asia/Kolkata')
    
    def scheduled_post():
        if 'bot' in st.session_state:
            bot = st.session_state.bot
            trending = bot.get_trending_topics()
            if trending:
                topic = trending[0]  # Use first trending topic
                content_ideas = bot.search_topic_content(topic)
                if content_ideas:
                    # Post the first highly recommended content
                    recommended = [idea for idea in content_ideas if idea['recommended']]
                    if recommended:
                        success, message = bot.post_tweet(recommended[0]['content'])
                        st.session_state.last_scheduled_post = {
                            'time': datetime.now(ist),
                            'success': success,
                            'message': message,
                            'content': recommended[0]['content']
                        }
    
    # Schedule for 10 AM IST daily
    schedule.every().day.at("10:00").do(scheduled_post)
    
    # Run scheduler in background
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

def main():
    st.set_page_config(
        page_title="Twitter Automation Bot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Twitter Automation Bot Dashboard")
    st.markdown("Intelligent Twitter posting with sentiment analysis and trend monitoring")
    
    # Initialize bot
    if 'bot' not in st.session_state:
        st.session_state.bot = StreamlitTwitterBot()
        setup_scheduler()
    
    bot = st.session_state.bot
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a feature", [
        "Manual Posting",
        "Trend-Based Content",
        "Analytics Dashboard",
        "Scheduled Posts",
        "Bot Status"
    ])
    
    if page == "Manual Posting":
        st.header("Manual Tweet Posting")
        
        # Manual text input
        manual_content = st.text_area("Enter your tweet content:", height=100, max_chars=280)
        
        if manual_content:
            # Show character count
            char_count = len(manual_content)
            if char_count > 280:
                st.error(f"Tweet too long: {char_count}/280 characters")
            else:
                st.info(f"Characters: {char_count}/280")
                
                # Analyze sentiment
                sentiment_result = bot.sentiment_analyzer.analyze_sentiment(manual_content)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sentiment", sentiment_result['sentiment'].title())
                with col2:
                    st.metric("Confidence", f"{sentiment_result['confidence']:.2f}")
                with col3:
                    color = "green" if sentiment_result['sentiment'] == 'positive' else "orange" if sentiment_result['sentiment'] == 'neutral' else "red"
                    st.markdown(f"<div style='color: {color}'>●</div>", unsafe_allow_html=True)
                
                if st.button("Post Tweet", type="primary"):
                    success, message = bot.post_tweet(manual_content)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
    
    elif page == "Trend-Based Content":
        st.header("Trend-Based Content Generation")
        
        # Topic input
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input("Enter a topic to search:", placeholder="e.g., Artificial Intelligence")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            use_trending = st.button("Use Trending Topic")
        
        if use_trending:
            trending = bot.get_trending_topics()
            if trending:
                topic = trending[0]
                st.info(f"Using trending topic: {topic}")
        
        if topic:
            st.subheader(f"Content Ideas for: {topic}")
            
            with st.spinner("Generating content ideas..."):
                content_ideas = bot.search_topic_content(topic)
            
            # Display content options
            for idea in content_ideas:
                with st.expander(f"Option {idea['id']} - {idea['sentiment'].title()} ({idea['confidence']:.2f})"):
                    st.write(idea['content'])
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button(f"Post {idea['id']}", key=f"post_{idea['id']}"):
                            success, message = bot.post_tweet(idea['content'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col2:
                        if idea['recommended']:
                            st.success("Recommended")
                        else:
                            st.warning("Review suggested")
            
            if st.button("Generate More Options"):
                st.rerun()
    
    elif page == "Analytics Dashboard":
        st.header("Analytics Dashboard")
        
        # Get analytics data
        daily_stats = bot.analytics.get_daily_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tweets Today", daily_stats.get('tweets_posted', 0))
        with col2:
            st.metric("Replies Today", daily_stats.get('replies_sent', 0))
        with col3:
            st.metric("Daily Limit", "16")
        with col4:
            remaining = 16 - daily_stats.get('tweets_posted', 0)
            st.metric("Remaining", max(0, remaining))
        
        # Show recent activity
        st.subheader("Recent Activity")
        analytics_data = bot.analytics.get_stats()
        
        if analytics_data.get('tweets', []):
            for tweet in analytics_data['tweets'][-5:]:  # Last 5 tweets
                st.text(f"Tweet ID: {tweet.get('id', 'N/A')} - {tweet.get('timestamp', 'N/A')}")
        else:
            st.info("No recent tweets to display")
    
    elif page == "Scheduled Posts":
        st.header("Scheduled Posts")
        
        st.info("Automatic posting scheduled daily at 10:00 AM IST")
        
        # Show last scheduled post if available
        if 'last_scheduled_post' in st.session_state:
            last_post = st.session_state.last_scheduled_post
            st.subheader("Last Scheduled Post")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Time:** {last_post['time'].strftime('%Y-%m-%d %H:%M:%S IST')}")
                st.write(f"**Status:** {'Success' if last_post['success'] else 'Failed'}")
            with col2:
                st.write(f"**Content:** {last_post['content'][:100]}...")
                st.write(f"**Message:** {last_post['message']}")
        
        # Next scheduled time
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        next_post = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if next_post <= now:
            next_post += timedelta(days=1)
        
        st.write(f"**Next scheduled post:** {next_post.strftime('%Y-%m-%d %H:%M:%S IST')}")
    
    elif page == "Bot Status":
        st.header("Bot Status")
        
        # API Status
        if bot.client:
            st.success("Twitter API: Connected")
            try:
                me = bot.client.get_me()
                st.info(f"Authenticated as: @{me.data.username}")
            except:
                st.warning("Authentication may have issues")
        else:
            st.error("Twitter API: Disconnected")
        
        # Sentiment Analysis Status
        st.success("Sentiment Analysis: Active")
        st.info("Using VADER and TextBlob multi-layered analysis")
        
        # Scheduler Status
        st.success("Scheduler: Running")
        st.info("Daily posts scheduled at 10:00 AM IST")
        
        # Test sentiment analysis
        st.subheader("Test Sentiment Analysis")
        test_text = st.text_input("Enter text to analyze:")
        if test_text:
            result = bot.sentiment_analyzer.analyze_sentiment(test_text)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sentiment:** {result['sentiment']}")
            with col2:
                st.write(f"**Confidence:** {result['confidence']:.3f}")

if __name__ == "__main__":
    main()
