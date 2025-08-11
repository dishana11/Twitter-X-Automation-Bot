import os
import json
import tweepy
import argparse
from pathlib import Path

# Config
SCHEDULE_FILE = Path("scheduled_tweets.json")

# Twitter Auth
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_CONSUMER_KEY"),
    os.getenv("TWITTER_CONSUMER_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth, wait_on_rate_limit=True)

def post_tweets(count):
    """Post tweets from schedule."""
    if not SCHEDULE_FILE.exists():
        print("❌ No scheduled tweets found.")
        return 0

    try:
        with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        tweets = data.get("tweets", [])
    except json.JSONDecodeError:
        print("❌ Corrupted JSON file.")
        return 0

    # Check Twitter API rate limits
    try:
        rate_limit = api.rate_limit_status()
        remaining = rate_limit['resources']['statuses']['/statuses/update']['remaining']
        if remaining < count:
            print(f"⚠️ Rate limit too low: {remaining} remaining, need {count}")
            return 0
    except Exception as e:
        print(f"❌ Error checking rate limits: {e}")
        return 0

    posted_count = 0
    for _ in range(min(count, len(tweets))):
        tweet = tweets.pop(0)
        try:
            api.update_status(tweet)
            print(f"✅ Posted: {tweet}")
            posted_count += 1
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            continue

    # Save remaining tweets
    if tweets:
        with SCHEDULE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"date": data.get("date", ""), "tweets": tweets}, f, indent=2, ensure_ascii=False)
    else:
        SCHEDULE_FILE.unlink(missing_ok=True)

    print(f"📢 Finished posting {posted_count} tweet(s).")
    return posted_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of tweets to post")
    args = parser.parse_args()

    post_tweets(args.count)
