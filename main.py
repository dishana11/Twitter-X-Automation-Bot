import os
import tweepy

def main():
    # Get API keys from environment variables
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    # Authenticate to Twitter
    auth = tweepy.OAuth1UserHandler(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
    )
    api = tweepy.API(auth)

    try:
        # Post a tweet
        api.update_status("Hello world from my AI bot! 🤖 #AITweetTest")
        print("Tweet posted successfully!")
    except tweepy.TweepError as e:
        print(f"Error posting tweet: {e}")

if __name__ == "__main__":
    main()
