import os
import json
import tweepy
import argparse
from pathlib import Path
from datetime import datetime

# Config
SCHEDULE_FILE = Path("scheduled_tweets.json")
LOG_FILE = Path("tweet_post_log.txt")

# Validate Twitter API credentials
required_env = ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
for env in required_env:
    if not os.getenv(env):
        print(f"❌ Missing environment variable: {env}")
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.utcnow()}: Missing env var {env}\n")
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
        print("❌ No scheduled tweets found.")
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.utcnow()}: No scheduled tweets found\n")
        return 0

    try:
        with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        tweets = data.get("tweets", [])
    except json.JSONDecodeError:
        print("❌ Corrupted JSON file.")
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.utcnow()}: Corrupted JSON file\n")
        return 0

    posted_count = 0
    for _ in range(min(count, len(tweets))):
        tweet = tweets.pop(0)
        try:
            response = client.create_tweet(text=tweet)
            tweet_id = response.data['id']
            print(f"✅ Posted: {tweet} (ID: {tweet_id})")
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.utcnow()}: Posted tweet: {tweet} (ID: {tweet_id})\n")
            posted_count += 1
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.utcnow()}: Error posting tweet: {e}\n")
            continue

    # Save remaining tweets
    if tweets:
        with SCHEDULE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"date": data.get("date", ""), "tweets": tweets}, f, indent=2, ensure_ascii=False)
    else:
        SCHEDULE_FILE.unlink(missing_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.utcnow()}: Deleted empty scheduled_tweets.json\n")

    print(f"📢 Finished posting {posted_count} tweet(s).")
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.utcnow()}: Finished posting {posted_count} tweet(s)\n")
    return posted_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of tweets to post")
    args = parser.parse_args()

    post_tweets(args.count)
