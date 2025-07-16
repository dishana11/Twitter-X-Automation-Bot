import tweepy, json, os
from datetime import datetime

with open("scheduled_tweets.json") as f:
    data = json.load(f)

tweets = data.get("tweets", [])[:20]
index = datetime.utcnow().hour - 4
if index < 0 or index >= len(tweets):
    print("⚠️ No tweet scheduled for this hour.")
    exit(0)

tweet = tweets[index]

client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

try:
    client.create_tweet(text=tweet)
    print("✅ Tweet posted:", tweet)
except Exception as e:
    print("❌ Failed to post:", e)
    exit(1)
