import os
import json
import re
import time
import argparse
from datetime import datetime
from pathlib import Path
import nltk

# Ensure required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--batch-size", type=int, default=15, help="Number of tweets to generate per batch")
parser.add_argument("--max-tweets", type=int, default=100, help="Maximum number of tweets to generate")
args = parser.parse_args()

# Path to store tweets
output_file = Path("scheduled_tweets.json")
today = datetime.utcnow().strftime("%Y-%m-%d")

# Check if we already have enough tweets for today
if output_file.exists():
    try:
        existing = json.load(output_file.open())
        if existing.get("date") == today and len(existing.get("tweets", [])) >= args.max_tweets:
            print(f"✅ Already have {len(existing.get('tweets', []))} tweets for today.")
            exit(0)
    except json.JSONDecodeError:
        print("⚠️ Corrupted JSON file. Will overwrite.")

# Prompt for LLMs
prompt = """
You are a witty, casual social media creator who writes posts for X.com (Twitter). Your posts should be:
- Primarily engaging questions that spark conversation across various fields (tech, science, arts, business, etc.)
- Questions should be thought-provoking but accessible to people from different backgrounds
- Include real-life questions like "What's one thing you regret doing?" or "What's the best advice you've ever received?"
- Format as 1-3 line questions that encourage responses
- Absolutely NO hashtags in any posts
- Vary the style throughout the day: some should be curious, some playful, some philosophical
- Questions should feel human and conversational, like you're genuinely curious
- Some examples: 
  "What's one technology you think will disappear in 5 years?" 
  "If you could have dinner with any historical figure, who would it be and why?"
  "What's something you believed as a child that turned out to be completely wrong?"
  "What's one skill you think everyone should learn?"

Format your output exactly like this, numbering posts sequentially:
---
Post 1:
[Your engaging question here]

Post 2:
[Your engaging question here]

Post 3:
[Your engaging question here]
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()
batch_size = args.batch_size
max_tweets = args.max_tweets
num_batches = (max_tweets + batch_size - 1) // batch_size  # Calculate needed batches

# If we already have some tweets, load them
if output_file.exists():
    try:
        existing_data = json.load(output_file.open())
        if existing_data.get("date") == today:
            all_tweets = existing_data.get("tweets", [])
            seen = set(tweet["text"] for tweet in all_tweets)
            print(f"📊 Loaded {len(all_tweets)} existing tweets for today.")
    except json.JSONDecodeError:
        print("⚠️ Corrupted JSON file. Starting fresh.")

# Validate environment variables
required_env = ["GOOGLE_GEMINI", "OPENAI_API_KEY"]
for env in required_env:
    if not os.getenv(env):
        print(f"❌ Missing environment variable: {env}")
        exit(1)

# Try Gemini API first
raw_text = ""
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    print("✅ Using Google Gemini API")
except Exception as e:
    print(f"⚠️ Gemini setup failed: {e}")

# Fallback to OpenAI if Gemini fails
if 'model' not in locals():
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        print("✅ Using OpenAI API")
    except Exception as e:
        print(f"❌ Both Gemini and OpenAI setup failed: {e}")
        exit(1)

# Batch generation (no rate limiting for premium accounts)
for batch in range(num_batches):
    if len(all_tweets) >= max_tweets:
        break
        
    print(f"Generating batch {batch + 1}/{num_batches}...")
    try:
        if 'model' in locals():
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            print(f"✅ Gemini batch {batch + 1} successful.")
        else:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Using GPT-4 for premium quality
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            raw_text = response.choices[0].message.content.strip()
            print(f"✅ OpenAI batch {batch + 1} successful.")
    except Exception as e:
        print(f"❌ Batch {batch + 1} failed: {e}")
        continue

    # Log raw response for debugging
    with open("raw_response_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow()}: Batch {batch + 1} response:\n{raw_text}\n\n")

    # Extract tweets
    pattern = re.compile(r"Post \d+:\s*\n((?:.*\n)*?)(?=\nPost \d+:\s*\n|\Z)", re.DOTALL)
    matches = pattern.findall(raw_text)

    if not matches:
        print(f"❌ Failed to parse posts in batch {batch + 1}.")
        continue

    # Filter tweets
    for post_text in matches:
        tweet_text = post_text.strip()
        if tweet_text and tweet_text not in seen:
            all_tweets.append({"text": tweet_text, "image_suggestion": None})
            seen.add(tweet_text)
            print(f"➕ Added tweet: {tweet_text[:50]}...")

    # Stop if enough tweets
    if len(all_tweets) >= max_tweets:
        break

# Fallback tweets if we don't have enough
default_tweets = [
    "What's one piece of advice you'd give to your younger self?",
    "If you could master any skill instantly, what would it be and why?",
    "What's something you believed as a child that turned out to be completely wrong?",
    "What's the most important lesson you've learned from a failure?",
    "What book has had the biggest impact on your life?",
    "If you could have a conversation with anyone living or dead, who would it be?",
    "What's a simple pleasure that always makes your day better?",
    "What's something you've been meaning to try but haven't gotten around to yet?"
]

while len(all_tweets) < max_tweets:
    fallback = default_tweets[len(all_tweets) % len(default_tweets)]
    if fallback not in seen:
        all_tweets.append({"text": fallback, "image_suggestion": None})
        seen.add(fallback)
        print(f"➕ Added fallback tweet: {fallback}")

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:max_tweets]
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_tweets[:max_tweets])} tweets to '{output_file.name}'.")
except Exception as e:
    print(f"❌ Failed to save tweets: {e}")
    exit(1)
