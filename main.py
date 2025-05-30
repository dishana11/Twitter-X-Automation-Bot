import os
import sys
import requests
import tweepy

# --- Twitter Auth ---
TWITTER_API_KEY = os.getenv("CONSUMER_KEY")
TWITTER_API_SECRET = os.getenv("CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_SAMAPI_KEY = os.getenv("OPENAI_SAMAPI_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

def twitter_auth():
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    return tweepy.API(auth)

def generate_with_openai(prompt, api_key):
    url = "https://api.openai.com/v1/completions"
    data = {
        "model": "text-davinci-003",
        "prompt": f"Write a concise, engaging tweet about: {prompt}",
        "max_tokens": 60,
        "temperature": 0.8,
        "n": 1,
        "stop": None
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers, timeout=12)
    if response.status_code == 429 or "quota" in response.text.lower():
        raise RuntimeError("OpenAI quota exceeded or rate limited")
    response.raise_for_status()
    return response.json()["choices"][0]["text"].strip()

def generate_with_claude(prompt):
    url = "https://api.anthropic.com/v1/complete"
    data = {
        "model": "claude-3-opus-20240229",
        "prompt": f"\n\nHuman: Write a concise, engaging tweet about: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 60,
        "temperature": 0.8,
        "stop_sequences": ["\n\nHuman:"]
    }
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers, timeout=12)
    response.raise_for_status()
    return response.json()["completion"].strip()

def generate_tweet(prompt):
    try:
        tweet = generate_with_openai(prompt, OPENAI_API_KEY)
        print("Generated with OpenAI (main key).")
        return tweet[:280]
    except Exception as e:
        print(f"OpenAI main key failed: {e}")
    try:
        tweet = generate_with_openai(prompt, OPENAI_SAMAPI_KEY)
        print("Generated with OpenAI (backup key).")
        return tweet[:280]
    except Exception as e:
        print(f"OpenAI backup key failed: {e}")
    try:
        tweet = generate_with_claude(prompt)
        print("Generated with Claude.")
        return tweet[:280]
    except Exception as e:
        print(f"Claude failed: {e}")
        return f"Unable to generate tweet at this time. (Error: {e})"

def post_tweet(api, text):
    try:
        api.update_status(text)
        print("Tweet posted successfully.")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def manual_prompt_tweet():
    if len(sys.argv) > 2:
        prompt = sys.argv[2]
    else:
        prompt = os.getenv("PROMPT")
    if not prompt:
        try:
            prompt = input("Enter a prompt for your tweet: ")
        except EOFError:
            print("No prompt provided and cannot use input() in this environment.")
            return
    tweet_text = generate_tweet(prompt)
    print("Generated Tweet:\n", tweet_text)
    if os.getenv("CI"):  # GitHub Actions sets CI=true
        post_tweet(twitter_auth(), tweet_text)
    else:
        confirm = input("Post this tweet? (y/n): ").lower()
        if confirm == 'y':
            post_tweet(twitter_auth(), tweet_text)
        else:
            print("Tweet not posted.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Twitter Automation Bot (Manual Mode)")
    parser.add_argument("--mode", choices=["manual"], required=True,
                        help="Run in 'manual' mode only for this script")
    args = parser.parse_args()
    if args.mode == "manual":
        manual_prompt_tweet()
