import os
import json
import tweepy
from pathlib import Path

# ==== CONFIG ====
SCHEDULE_FILE = Path("scheduled_tweets.json")

# ==== TWITTER AUTH ====
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_CONSUMER_KEY"),
    os.getenv("TWITTER_CONSUMER_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)


def get_llm_tweet():
    """Fallback tweet generator if schedule file is empty."""
    prompt = (
        "Write a short, casual tweet in the style:\n"
        "1st person thoughts\n"
        "Techy / curious tone\n"
        "No emojis\n"
        "One hashtag at the end"
    )

    # --- Gemini ---
    try:
        from google.generativeai import GenerativeModel, configure
        configure(api_key=os.getenv("GOOGLE_GEMINI"))
        model = GenerativeModel("gemini-2.0-pro")
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        pass

    # --- OpenAI ---
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        pass

    # --- OpenAI SAM ---
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_SAM_KEY")
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        pass

    # --- Claude ---
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        resp = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception:
        pass

    return None


def post_tweet():
    """Post one tweet from schedule and remove it."""
    if SCHEDULE_FILE.exists():
        try:
            with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            tweets = data.get("tweets", [])
        except json.JSONDecodeError:
            tweets = []
    else:
        tweets = []

    # If empty, try generating one
    if not tweets:
        print("⚠️ No scheduled tweets found — generating one...")
        tweet = get_llm_tweet()
        if not tweet:
            print("❌ All LLMs failed — no tweet posted.")
            return
    else:
        tweet = tweets.pop(0)

    # Post to Twitter
    try:
        api.update_status(tweet)
        print(f"✅ Posted: {tweet}")
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return

    # Save remaining tweets
    if tweets:
        with SCHEDULE_FILE.open("w", encoding="utf-8") as f:
            json.dump({"date": data.get("date", ""), "tweets": tweets}, f, indent=2, ensure_ascii=False)
    else:
        # Remove file if empty
        SCHEDULE_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    post_tweet()
