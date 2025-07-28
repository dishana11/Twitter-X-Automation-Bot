import os
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Twitter API
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_CONSUMER_KEY"),
    os.getenv("TWITTER_CONSUMER_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
model = genai.GenerativeModel('gemini-pro')

# Prompt for tweet generation
prompt = "Generate a short, creative, and engaging tweet about AI, technology, or space. Keep it under 280 characters. Use emojis and sound human."

# Get response
response = model.generate_content(prompt)
tweet = response.text.strip()

# Make sure it's short enough
if len(tweet) > 280:
    tweet = tweet[:277] + "..."

# Post to Twitter
api.update_status(tweet)
print("Tweet posted:", tweet)
