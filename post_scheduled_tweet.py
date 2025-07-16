import tweepy, json, os
from datetime import datetime 
from pathlib import Path
 
# Load tweets
output_file = Path("scheduled_tweets.json")
if not output_file.exists():
    print("❌ scheduled_tweets.json not found.")
    exit(1)

with open(output_file) as f:
    data = json.load(f)
    tweets = data.get("tweets", [])

# Determine index
index = datetime.utcnow().hour - 4  # since your cron starts at 4:30 UTC
if index < 0 or index >= len(tweets):
    print("⚠️ No tweet scheduled for this hour.")
    exit(0)

tweet = tweets[index]

# Setup client
client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Post
try:
    client.create_tweet(text=tweet)
    print("✅ Tweet posted:", tweet)
except Exception as e:
    print("❌ Failed to post tweet:", e)
    exit(1)
