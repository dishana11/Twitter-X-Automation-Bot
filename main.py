import os
import requests
import tweepy

# Twitter auth setup
auth = tweepy.OAuth1UserHandler(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth)

# Claude API setup
claude_api_key = os.environ.get("CLAUDE_API_KEY")
if not claude_api_key or not claude_api_key.strip():
    raise ValueError("CLAUDE_API_KEY is not set or is invalid.")
print(f"Using CLAUDE_API_KEY: {claude_api_key[:4]}...")  # Safe debug output

claude_api_url = "https://api.anthropic.com/v1/claude-3.7/sonnet/completions"
custom_prompt = os.getenv("CUSTOM_PROMPT", "Write a short, fun, science-themed tweet with an emoji.")

payload = {
    "model": "claude-3.7-sonnet",
    "prompt": custom_prompt,
    "max_tokens": 100
}

headers = {
    "Authorization": f"Bearer {claude_api_key}",
    "Content-Type": "application/json"
}

response = requests.post(claude_api_url, json=payload, headers=headers)
if response.status_code != 200:
    print(f"API call failed with {response.status_code}: {response.text}")
    response.raise_for_status()

response_data = response.json()
tweet = response_data.get("choices", [{}])[0].get("text", "").strip()

if tweet:
    api.update_status(tweet)
    print("Tweet posted:", tweet)
else:
    print("Failed to generate a tweet.")
