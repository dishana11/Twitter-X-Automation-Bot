import os
import json
import argparse
import tempfile
import random
import requests
import tweepy
from pathlib import Path
from datetime import datetime

# Config
SCHEDULE_FILE = Path("scheduled_tweets.json")
LOG_FILE = Path("tweet_post_log.txt")
MAX_IMAGES_PER_RUN = 2
IMAGE_PROBABILITY = 0.2  # ~20% chance for tweets with image suggestions

# Validate required Twitter environment variables
required_twitter_env = ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET",
                        "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
for env in required_twitter_env:
    if not os.getenv(env):
        print(f"❌ Missing environment variable: {env}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow()}: Missing env var {env}\n")
        exit(1)

# Initialize Twitter API
auth = tweepy.OAuth1UserHandler(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
client_v2 = tweepy.Client(
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=True
)

# Check if OpenAI API key is available (optional for image generation)
OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
if OPENAI_AVAILABLE:
    import openai
    from tenacity import retry, stop_after_attempt, wait_fixed
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    print("⚠️ OpenAI API key not available. Image generation disabled.")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow()}: OpenAI API key not available. Image generation disabled.\n")

if OPENAI_AVAILABLE:
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def generate_image(prompt):
        """Generate image with DALL-E and return temporary file path."""
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            url = response['data'][0]['url']
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_file.write(r.content)
            tmp_file.close()
            return tmp_file.name, url
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def post_tweet(client, text, media_ids=None):
    """Post a tweet with optional media."""
    try:
        if media_ids:
            return client.create_tweet(text=text, media_ids=media_ids)
        return client.create_tweet(text=text)
    except Exception as e:
        print(f"❌ Tweet posting failed: {e}")
        raise

def post_tweets(count):
    """Post tweets from schedule, with images for ~20% of tweets with suggestions."""
    if not SCHEDULE_FILE.exists():
        print("❌ No scheduled tweets found.")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow()}: No scheduled tweets found\n")
        return 0

    try:
        with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        tweets = data.get("tweets", [])
    except json.JSONDecodeError:
        print("❌ Corrupted JSON file.")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow()}: Corrupted JSON file\n")
        return 0

    posted_count = 0
    images_posted = 0

    for _ in range(min(count, len(tweets))):
        tweet = tweets.pop(0)
        text = tweet["text"]
        image_suggestion = tweet.get("image_suggestion")

        media_ids = None
        if (OPENAI_AVAILABLE and image_suggestion and
            images_posted < MAX_IMAGES_PER_RUN and
            random.random() < IMAGE_PROBABILITY):
            try:
                img_path, img_url = generate_image(image_suggestion)
                if img_path:
                    media = api_v1.media_upload(img_path)
                    media_ids = [media.media_id]
                    images_posted += 1
                    os.unlink(img_path)
                    print(f"✅ Generated image: {img_url}")
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"{datetime.utcnow()}: Generated image: {img_url}\n")
            except Exception as e:
                print(f"❌ Image upload failed: {e}")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{datetime.utcnow()}: Image upload failed: {e}\n")

        try:
            response = post_tweet(client_v2, text, media_ids)
            tweet_id = response.data['id']
            print(f"✅ Posted: {text} (ID: {tweet_id})")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.utcnow()}: Posted tweet: {text} (ID: {tweet_id})\n")
            posted_count += 1
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.utcnow()}: Error posting tweet: {e}\n")
            continue

    if tweets:
        with SCHEDULE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"date": data.get("date", ""), "tweets": tweets}, f, indent=2, ensure_ascii=False)
    else:
        SCHEDULE_FILE.unlink(missing_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow()}: Deleted empty scheduled_tweets.json\n")

    print(f"📢 Finished posting {posted_count} tweet(s), {images_posted} with images.")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow()}: Finished posting {posted_count} tweet(s), {images_posted} with images\n")
    return posted_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=8, help="Number of tweets to post")
    args = parser.parse_args()

    post_tweets(args.count)
