# post_scheduled_tweet.py

import tweepy
import os
from dotenv import load_dotenv

# Load API credentials from .env
load_dotenv()

auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# Read generated tweets
try:
    with open("scheduled_tweets.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("❌ Error: scheduled_tweets.txt file not found.")
    exit(1)

# Split tweets using custom delimiter
raw_tweets = content.split("---TWEET---")[1:]  # Skip the first empty split

for raw in raw_tweets:
    try:
        tweet_block = raw.split("---END---")[0].strip()
        lines = tweet_block.split("\n")

        tweet_text = ""
        for line in lines:
            if line.startswith("Tweet"):
                tweet_text = line.replace("Tweet 1:", "").replace("Tweet 2:", "").replace("Tweet 3:", "").replace("Tweet 4:", "").replace("Tweet 5:", "")
                tweet_text = tweet_text.replace("Tweet:", "").strip()
                break

        if tweet_text:
            api.update_status(tweet_text)
            print(f"✅ Tweeted:\n{tweet_text}\n")
        else:
            print("⚠️ No tweet content found:\n", tweet_block)

    except Exception as e:
        print("❌ Error posting tweet:", e)
