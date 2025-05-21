import os
import requests
import tweepy

# Twitter authentication
auth = tweepy.OAuth1UserHandler(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

# Claude 3.7 Sonnet API endpoint and key
claude_api_url = "https://api.anthropic.com/v1/claude-3.7/sonnet/completions"
claude_api_key = os.environ["CLAUDE_API_KEY"]

# Get custom prompt from GitHub Actions input
custom_prompt = os.getenv("CUSTOM_PROMPT", "Write a short, fun, science-themed tweet with an emoji.")

# Prepare the request payload
payload = {
    "model": "claude-3.7-sonnet",
    "prompt": custom_prompt,
    "max_tokens": 100
}

headers = {
    "Authorization": f"Bearer {claude_api_key}",
    "Content-Type": "application/json"
}

# Generate tweet using Claude 3.7 Sonnet
response = requests.post(claude_api_url, json=payload, headers=headers)
response_data = response.json()

tweet = response_data.get("choices", [{}])[0].get("text", "").strip()

if tweet:
    # Post the tweet
    api.update_status(tweet)
    print("Tweet posted:", tweet)
else:
    print("Failed to generate a tweet.")
