```python
import os
import json
import tweepy
import argparse
from pathlib import Path
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging

# Set up logging
logging.basicConfig(filename='tweet_post_log.txt', level=logging.INFO, 
                    format='%(asctime)s: %(message)s')

# Config
SCHEDULE_FILE = Path("scheduled_tweets.json")
LOG_FILE = Path("tweet_post_log.txt")

# Initialize sentiment analyzer
try:
    import nltk
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Validate Twitter API credentials
required_env = ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
for env in required_env:
    if not os.getenv(env):
        logging.error(f"Missing environment variable: {env}")
        print(f"❌ Missing environment variable: {env}")
        exit(1)

# Twitter API v2 Client
client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=True
)

def post_tweets(count):
    """Post tweets from schedule."""
    if not SCHEDULE_FILE.exists():
        logging.error("No scheduled tweets found.")
        print("❌ No scheduled tweets found.")
        return 0

    try:
        with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        tweets = data.get("tweets", [])
        if not tweets:
            logging.error("No tweets in scheduled_tweets.json.")
            print("❌ No tweets in scheduled_tweets.json.")
            return 0
    except json.JSONDecodeError:
        logging.error("Corrupted JSON file.")
        print("❌ Corrupted JSON file.")
        return 0

    posted_count = 0
    for _ in range(min(count, len(tweets))):
        tweet = tweets.pop(0)
        tweet_text = tweet["text"]
        if not (500 <= len(tweet_text) <= 600):
            logging.warning(f"Skipped tweet (invalid length: {len(tweet_text)} characters).")
            print(f"⛔ Skipped tweet (invalid length: {len(tweet_text)} characters).")
            continue
        if sia.polarity_scores(tweet_text)["compound"] < 0.1:
            logging.warning(f"Skipped tweet (low sentiment score).")
            print(f"⚠️ Skipped tweet (low sentiment score).")
            continue
        try:
            response = client.create_tweet(text=tweet_text)
            tweet_id = response.data['id']
            logging.info(f"Posted tweet: {tweet_text} (ID: {tweet_id})")
            print(f"✅ Posted: {tweet_text} (ID: {tweet_id})")
            posted_count += 1
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
            print(f"❌ Error posting tweet: {e}")
            continue

    # Save remaining tweets
    try:
        if tweets:
            with SCHEDULE_FILE.open("w", encoding="utf-8") as f:
                json.dump({"date": data.get("date", ""), "tweets": tweets}, f, indent=2, ensure_ascii=False)
        else:
            SCHEDULE_FILE.unlink(missing_ok=True)
            logging.info("Deleted empty scheduled_tweets.json")
            print("🗑️ Deleted empty scheduled_tweets.json")
    except Exception as e:
        logging.error(f"Failed to save updated tweets: {e}")
        print(f"❌ Failed to save updated tweets: {e}")
        return posted_count

    logging.info(f"Finished posting {posted_count} tweet(s).")
    print(f"📢 Finished posting {posted_count} tweet(s).")
    return posted_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=2, help="Number of tweets to post")
    args = parser.parse_args()
    post_tweets(args.count)
```
