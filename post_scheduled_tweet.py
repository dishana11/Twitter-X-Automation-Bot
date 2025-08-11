import json
import os
import requests
from pathlib import Path

# ==== CONFIG ====
SCHEDULE_FILE = Path("scheduled_tweets.json")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# OpenAI API (primary & secondary)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_PRIMARY = "gpt-4o-mini"
OPENAI_MODEL_SECONDARY = "gpt-3.5-turbo"

# Claude API
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# ==== FUNCTIONS ====
def load_scheduled_tweets():
    if not SCHEDULE_FILE.exists():
        return []
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_scheduled_tweets(tweets):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

def post_to_twitter(tweet_text):
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"text": tweet_text}
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

# ==== AI HELPERS ====
def generate_with_gemini(prompt):
    try:
        r = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[Gemini] Failed: {e}")
        return None

def generate_with_openai(prompt, model):
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[OpenAI {model}] Failed: {e}")
        return None

def generate_with_claude(prompt):
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={"model": "claude-3-opus-20240229", "max_tokens": 200, "messages": [{"role": "user", "content": prompt}]},
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        print(f"[Claude] Failed: {e}")
        return None

# ==== MAIN ====
def main():
    tweets = load_scheduled_tweets()
    if not tweets:
        print("No scheduled tweets found.")
        return

    tweet_data = tweets[0]
    prompt = tweet_data.get("prompt") or tweet_data.get("text")

    generated_text = (
        generate_with_gemini(prompt)
        or generate_with_openai(prompt, OPENAI_MODEL_PRIMARY)
        or generate_with_openai(prompt, OPENAI_MODEL_SECONDARY)
        or generate_with_claude(prompt)
    )

    if not generated_text:
        print("All models failed.")
        return

    # Post to Twitter
    try:
        post_to_twitter(generated_text)
        print("Tweet posted successfully:", generated_text)
        # Remove the posted tweet from list
        tweets.pop(0)
        save_scheduled_tweets(tweets)
    except Exception as e:
        print(f"Failed to post tweet: {e}")

if __name__ == "__main__":
    main()
