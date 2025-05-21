import os
import openai
import tweepy

# Twitter authentication
auth = tweepy.OAuth1UserHandler(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

# OpenAI authentication
openai.api_key = os.environ["OPENAI_API_KEY"]

# Get custom prompt from GitHub Actions input
custom_prompt = os.getenv("CUSTOM_PROMPT")

if custom_prompt:
    prompt = custom_prompt
else:
    prompt = "Write a short, fun, science-themed tweet with an emoji."

# Generate tweet using OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=50
)

tweet = response['choices'][0]['message']['content'].strip()

# Post the tweet
api.update_status(tweet)
print("Tweet posted:", tweet)
