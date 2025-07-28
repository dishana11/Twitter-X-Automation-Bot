import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve Twitter credentials from environment
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Check if all credentials are present
if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    print("❌ Error: One or more Twitter API credentials are missing in the .env file.")
    exit(1)

# Set up Tweepy authentication
try:
    auth = tweepy.OAuth1UserHandler(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth)
    api.verify_credentials()
    print("✅ Twitter authentication successful.")
except Exception as e:
    print(f"❌ Twitter authentication failed: {e}")
    exit(1)

# Read and post tweets from scheduled_tweets.txt
tweet_file = "scheduled_tweets.txt"

try:
    with open(tweet_file, "r") as file:
        tweets = file.readlines()

    if not tweets:
        print("⚠️ No tweets found in scheduled_tweets.txt.")
        exit(0)

    for tweet in tweets:
        tweet = tweet.strip()
        if tweet:
            try:
                api.update_status(tweet)
                print(f"✅ Tweet posted: {tweet}")
            except Exception as e:
                print(f"❌ Failed to post tweet: {tweet}\n   ↳ Error: {e}")
except FileNotFoundError:
    print(f"❌ File not found: {tweet_file}")
