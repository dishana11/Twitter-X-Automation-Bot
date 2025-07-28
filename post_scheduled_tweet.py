# post_scheduled_tweet.py

import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

with open("scheduled_tweets.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Split tweets using our custom delimiter
raw_tweets = content.split("---TWEET---")[1:]

for raw in raw_tweets:
    try:
        tweet_block = raw.split("---END---")[0].strip()
        lines = tweet_block.split("\n")

        tweet_text = ""
        for line in lines:
            if line.startswith("Tweet:"):
                tweet_text = line.replace("Tweet:", "").strip()
                break

        if tweet_text:
            api.update_status(tweet_text)
            print(f"✅ Tweeted: {tweet_text}")
        else:
            print("⚠️ Tweet text not found in block:\n", tweet_block)

    except Exception as e:
        print("❌ Error posting tweet:", e)
