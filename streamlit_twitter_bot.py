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
from config.github_settings import get_github_config  # Import the GitHub config function
from utils.logger import get_logger

# Setup logger
logger = get_logger()

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
    
    # Load GitHub configuration
    github_config = get_github_config()
    auth_token = github_config['auth_token']

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

if __name__ == "__main__":
    main()
