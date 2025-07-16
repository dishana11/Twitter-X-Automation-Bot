import tweepy, json, os
from datetime import datetime

# Load scheduled tweets
with open("scheduled_tweets.json") as f:
    data = json.load(f)

tweets = data.get("tweets", [])[:5]  # ✅ LIMIT TO 5 tweets

# Determine which tweet to post based on current hour
# Assuming tweets go out at 5, 8, 11, 14, 17 UTC
schedule_hours = [5, 8, 11, 14, 17]
current_hour = datetime.utcnow().hour

try:
    index = schedule_hours.index(current_hour)
except ValueError:
    print("⚠️ No tweet scheduled for this hour.")
    exit(0)

tweet = tweets[index]

# Set up Twitter client
client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Try posting the tweet
try:
    client.create_tweet(text=tweet)
    print("✅ Tweet posted:", tweet)
except Exception as e:
    print("❌ Failed to post:", e)
    exit(1)
