#!/bin/bash
# Deployment script for Twitter Automation Bot

echo "🚀 Deploying Twitter Automation Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r deploy_requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Check environment variables
echo "🔑 Checking environment variables..."
if [ -z "$TWITTER_CONSUMER_KEY" ]; then
    echo "⚠️  TWITTER_CONSUMER_KEY not set"
fi

if [ -z "$TWITTER_CONSUMER_SECRET" ]; then
    echo "⚠️  TWITTER_CONSUMER_SECRET not set"
fi

if [ -z "$TWITTER_ACCESS_TOKEN" ]; then
    echo "⚠️  TWITTER_ACCESS_TOKEN not set"
fi

if [ -z "$TWITTER_ACCESS_TOKEN_SECRET" ]; then
    echo "⚠️  TWITTER_ACCESS_TOKEN_SECRET not set"
fi

if [ -z "$TWITTER_BEARER_TOKEN" ]; then
    echo "⚠️  TWITTER_BEARER_TOKEN not set"
fi

# Run the application
echo "🎯 Starting Twitter Automation Bot..."
streamlit run streamlit_twitter_bot.py --server.port=5000 --server.address=0.0.0.0
