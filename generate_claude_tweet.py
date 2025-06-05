import os
import requests
import json

prompt = os.environ["PROMPT"]

headers = {
    "Authorization": f"Bearer {os.environ['CLAUDE_API_KEY']}",
    "Content-Type": "application/json"
}

data = {
    "model": "claude-3-sonnet-20240229",  # Use the model name for Sonnet v3.7 or as required by your Claude provider
    "max_tokens": 150,
    "messages": [
        {
            "role": "user",
            "content": f"Write a concise, engaging tweet about: {prompt}. Include relevant, trending hashtags."
        }
    ]
}

response = requests.post(
    "https://api.anthropic.com/v1/messages",  # Change if using OpenRouter or another Claude API provider
    headers=headers,
    data=json.dumps(data)
)

if response.status_code != 200:
    print("Claude API call failed:", response.text)
    exit(1)

tweet = response.json()["choices"][0]["message"]["content"].strip()
print(f"Generated Tweet: {tweet}")

with open("generated_tweet.txt", "w") as f:
    f.write(tweet)
