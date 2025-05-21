import os
import tweepy
from openai import OpenAI

# Twitter authentication
auth = tweepy.OAuth1UserHandler(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get custom prompt from GitHub Actions input
custom_prompt = os.getenv("CUSTOM_PROMPT")

if custom_prompt:
    prompt = custom_prompt
else:
    prompt = "Write a short, fun, science-themed tweet with an emoji."

# Generate tweet using OpenAI
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
)

tweet = response.choices[0].message.content.strip()

# Post the tweet
api.update_status(tweet)
print("Tweet posted:", tweet)
