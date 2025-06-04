
# Twitter Automation Bot
A comprehensive Python Twitter automation bot with advanced features including multi-layered sentiment analysis, scheduled posting, auto-replies, hashtag monitoring, and analytics tracking.
## 🚀 Features
### Core Functionality
- **Scheduled Tweet Posting** - Schedule tweets for future posting
- **Auto-Reply System** - Automatically respond to mentions with intelligent replies
- **Hashtag Monitoring** - Track specified hashtags and identify engagement opportunities
- **Analytics Tracking** - Comprehensive performance metrics and reporting
- **Rate Limiting** - Built-in Twitter API rate limit compliance
### Advanced NLP Sentiment Analysis
Multi-layered fallback system for maximum reliability:
1. **VADER** (Primary) - Optimized for social media text, handles emojis and slang
2. **TextBlob** (Secondary) - Alternative sentiment analysis approach
3. **spaCy** (Tertiary) - Comprehensive NLP processing
4. **HuggingFace** (Final) - Advanced transformer-based analysis
## 📋 Requirements
- Python 3.11+
- Twitter Developer Account with API keys
- Required packages: `tweepy`, `textblob`, `vaderSentiment`
## ⚙️ Setup
1. **Get Twitter API Credentials**
   - Go to [developer.twitter.com](https://developer.twitter.com)
   - Create a Twitter Developer account
   - Create a new app/project
   - Get your API keys from the app dashboard
2. **Install Dependencies**
   ```bash
   pip install tweepy textblob vaderSentiment
   ```
3. **Configure Environment Variables**
   Set these environment variables with your Twitter API credentials:
   - `TWITTER_CONSUMER_KEY`
   - `TWITTER_CONSUMER_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `TWITTER_BEARER_TOKEN`
## 🎯 Usage
### Running the Bot
**Full Automation Mode** (recommended)
# Twitter Automation Bot with Streamlit Dashboard
A powerful Twitter automation bot with intelligent sentiment analysis, manual posting interface, scheduled tweets, and trend-based content generation.
## Features
- **Multi-layered Sentiment Analysis**: VADER and TextBlob fallback system
- **Interactive Streamlit Dashboard**: Web interface for easy management
- **Manual Posting**: Real-time sentiment analysis before posting
- **Trend-Based Content**: Generate 5 content options from any topic
- **Scheduled Posting**: Daily posts at 10 AM IST
- **Analytics Dashboard**: Track usage and performance
- **Free Tier Optimized**: Works with Twitter's Free API (500 posts/month)
## Quick Start
### 1. Fork this Repository
Click "Fork" to create your own copy of this repository.
### 2. Add Twitter API Secrets
Go to your forked repository → Settings → Secrets and variables → Actions → New repository secret
Add these secrets:
- `TWITTER_CONSUMER_KEY`: Your Twitter API Consumer Key
- `TWITTER_CONSUMER_SECRET`: Your Twitter API Consumer Secret
- `TWITTER_ACCESS_TOKEN`: Your Twitter Access Token
- `TWITTER_ACCESS_TOKEN_SECRET`: Your Twitter Access Token Secret
- `TWITTER_BEARER_TOKEN`: Your Twitter Bearer Token
### 3. Deploy to Streamlit Cloud
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Deploy your forked repository
4. Set the main file as: `streamlit_twitter_bot.py`
### 4. Local Development
```bash
python main.py --mode full --verbose
```
**Specific Modes**
# Clone your fork
git clone https://github.com/yourusername/twitter-automation-bot.git
cd twitter-automation-bot
# Install dependencies
pip install -r deploy_requirements.txt
# Set environment variables
export TWITTER_CONSUMER_KEY="your_key"
export TWITTER_CONSUMER_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"
export TWITTER_BEARER_TOKEN="your_bearer_token"
# Run locally
streamlit run streamlit_twitter_bot.py
```
## Getting Twitter API Credentials
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create a new app with "Read and Write" permissions
3. Generate your API keys and tokens
4. Make sure your Twitter account is public (not protected)
## Dashboard Features
### Manual Posting
- Type your content and get instant sentiment analysis
- Character counter (280 limit)
- Post only positive sentiment content
### Trend-Based Content
- Enter any topic (e.g., "Artificial Intelligence")
- Get 5 curated content options (A, B, C, D, E)
- Choose which ones to post with one click
- Generate more options if needed
### Analytics Dashboard
- View daily usage (posts used/remaining)
- Track weekly summaries
- Monitor bot performance
### Scheduled Posts
- Automatic posting at 10 AM IST daily
- Uses trending topics for content
- Sentiment-filtered content only
### Bot Status
- API connection monitoring
- Test sentiment analysis
- Real-time status updates
## API Limits
- **Free Tier**: 500 posts per month
- **Daily Budget**: 16 posts per day (conservative)
- **Rate Limiting**: Built-in protection
- **Duplicate Prevention**: Automatic detection
## Architecture
```
├── streamlit_twitter_bot.py    # Main Streamlit dashboard
├── bot/
│   ├── sentiment_analyzer.py  # Multi-layered sentiment analysis
│   ├── analytics.py           # Usage tracking and metrics
│   └── twitter_bot.py         # Core Twitter functionality
├── config/
│   ├── settings.py           # Configuration management
│   └── config.json           # Bot settings
├── utils/
│   ├── logger.py             # Logging utilities
│   └── rate_limiter.py       # Rate limiting
└── data/                     # Analytics and scheduling data
```
## Customization
### Modify Posting Schedule
Edit the scheduler in `streamlit_twitter_bot.py`:
```python
schedule.every().day.at("10:00").do(scheduled_post)  # Change time here
```
### Add Custom Content Templates
Modify `search_topic_content()` method to add your own content templates.
### Adjust Sentiment Thresholds
Change sentiment filtering in the posting methods.
## Troubleshooting
### Common Issues
1. **403 Forbidden Error**
   - Ensure your Twitter app has "Read and Write" permissions
   - Make your Twitter account public (not protected)
   - Regenerate API keys if needed
2. **Duplicate Content Error**
   - The bot prevents posting identical content
   - Modify your content slightly to make it unique
3. **Rate Limit Errors**
   - Built-in rate limiting should prevent this
   - Wait before retrying if encountered
### Support
- Check logs in the Streamlit interface
- Verify API credentials in Bot Status
- Test sentiment analysis functionality
## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
## License
MIT License - Feel free to use and modify for your projects.
## Deployment Options
### Streamlit Cloud (Recommended)
- Free hosting for public repositories
- Automatic updates from GitHub
- Built-in secret management
### Heroku
```bash
# Hashtag monitoring only
python main.py --mode monitor
# Scheduled posting only
python main.py --mode schedule
# Auto-replies only
python main.py --mode reply
```
### Demo and Testing
**Run Complete Demo**
```bash
python demo_bot.py
```
**Test Sentiment Analysis**
```bash
python test_sentiment.py
```
## 📊 Configuration
Edit `config/config.json` to customize:
```json
{
  "hashtag_monitoring": {
    "monitored_hashtags": ["#AI", "#Technology", "#Innovation"],
    "engagement_keywords": ["help", "question", "advice"]
  },
  "auto_replies": {
    "max_daily_replies": 50,
    "reply_check_interval_minutes": 3
  },
  "sentiment_analysis": {
    "enabled": true,
    "confidence_threshold": 0.5
  }
}
```
## 🧠 Sentiment Analysis Features
The bot uses a sophisticated 4-layer fallback system:
### VADER (Primary)
- Best for social media content
- Handles emojis, slang, and informal text
- Fast processing
- Designed specifically for Twitter-style content
### TextBlob (Secondary)
- Different algorithmic approach
- Good general-purpose sentiment analysis
- Reliable fallback option
### spaCy (Tertiary)
- Advanced NLP processing
- Comprehensive text analysis
- Available when spaCy models are installed
### HuggingFace (Final)
- State-of-the-art transformer models
- Most accurate but requires internet
- Uses free tier limits efficiently
## 📈 Analytics Dashboard
The bot tracks comprehensive metrics:
- **Daily Activity** - Tweets posted, replies sent
- **Engagement Metrics** - Response rates, interaction quality
- **Hashtag Performance** - Monitoring effectiveness
- **Sentiment Trends** - Analysis of processed content
- **Rate Limit Status** - API usage monitoring
Access analytics:
```python
from bot.analytics import AnalyticsTracker
analytics = AnalyticsTracker()
report = analytics.generate_report()
print(report)
```
## 🔧 Advanced Features
### Scheduled Posting
```python
from bot.scheduler import TweetScheduler
from datetime import datetime, timedelta
scheduler = TweetScheduler(api, config)
future_time = datetime.now() + timedelta(hours=2)
scheduler.schedule_tweet("Your tweet content", future_time)
```
### Custom Sentiment Analysis
```python
from bot.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
result = analyzer.analyze_sentiment("I love this new feature!")
print(f"Sentiment: {result['sentiment']}")
print(f"Method used: {result['method_used']}")
```
### Hashtag Monitoring
```python
from bot.hashtag_monitor import HashtagMonitor
monitor = HashtagMonitor(api, config)
monitor.add_hashtag("#NewTopic")
stats = monitor.get_hashtag_stats("#AI")
```
## 🛡️ Rate Limiting
The bot includes intelligent rate limiting:
- Respects Twitter API limits
- Automatic retry with exponential backoff
- Configurable limits for bot operations
- Real-time rate limit monitoring
## 📝 Logging
Comprehensive logging system:
- File-based logging with rotation
- Console output for real-time monitoring
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Performance metrics tracking
## 🚨 API Access Levels
The bot works with different Twitter API access levels:
- **Free Tier** - Limited functionality, basic posting
- **Basic Tier** - Enhanced features, more API calls
- **Pro Tier** - Full functionality, all features available
Some features may require higher access levels (mentions, trends, search).
## 🔍 Troubleshooting
**API Authentication Issues**
- Verify all 5 API credentials are set correctly
- Check Twitter Developer dashboard for app status
- Ensure API keys haven't expired
**Rate Limit Errors**
- Bot automatically handles rate limits
- Check `logs/` directory for detailed error information
- Consider upgrading Twitter API access level
**Sentiment Analysis Issues**
- VADER is the most reliable method
- TextBlob provides good fallback
- Check internet connection for HuggingFace
## 📚 File Structure
```
├── bot/                    # Main bot modules
│   ├── sentiment_analyzer.py  # Multi-layered sentiment analysis
│   ├── scheduler.py           # Tweet scheduling
│   ├── reply_handler.py       # Auto-reply system
│   ├── hashtag_monitor.py     # Hashtag tracking
│   ├── trend_analyzer.py      # Trend analysis
│   ├── analytics.py           # Performance tracking
│   └── twitter_bot.py         # Main bot orchestrator
├── config/                 # Configuration management
├── utils/                  # Utilities (logging, rate limiting)
├── data/                   # Data storage (JSON files)
├── logs/                   # Log files
├── main.py                 # Main entry point
├── demo_bot.py            # Feature demonstration
└── test_sentiment.py      # Sentiment analysis testing
```
## 🎉 Success Metrics
Your bot is successfully running when you see:
- ✅ Multi-layered sentiment analysis active
- ✅ Scheduled tweets processing
- ✅ Analytics tracking engagement
- ✅ Rate limiting preventing API issues
- ✅ Comprehensive logging for monitoring
## 🤝 Support
For issues or questions:
1. Check the l...
[truncated]
