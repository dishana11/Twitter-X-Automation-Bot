import tweepy
import json
import os
from datetime import datetime
from pathlib import Path

# Path to scheduled tweets file
output_file = Path("scheduled_tweets.json")

# Check if scheduled tweets exist
if not output_file.exists():
    print("❌ scheduled_tweets.json not found.")
    exit(1)

# Load scheduled tweets
with open(output_file, "r", encoding="utf-8") as f:
    try:
        data = json.load(f)
        tweets = data.get("tweets", [])
    except json.JSONDecodeError:
        print("❌ Failed to parse scheduled_tweets.json.")
        exit(1)

# Calculate which tweet to post
index = (datetime.utcnow().hour - 4) % len(tweets) if tweets else -1

if index == -1 or index >= len(tweets):
    print("⚠️ No tweet scheduled for this hour.")
    exit(0)

tweet = tweets[index].strip()

# Ensure tweet is not empty or too long
if not tweet:
    print("⚠️ Tweet content is empty.")
    exit(0)
elif len(tweet) > 280:
    print("⚠️ Tweet exceeds 280 characters.")
    exit(0)

# Authenticate Twitter client
try:
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
except Exception as e:
    print("❌ Twitter client setup failed:", e)
    exit(1)

# Post the tweet
try:
    client.create_tweet(text=tweet)
    print("✅ Tweet posted successfully:", tweet)
except Exception as e:
    print("❌ Failed to post tweet:", e)
    exit(1)
