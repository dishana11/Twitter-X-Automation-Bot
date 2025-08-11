import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
import nltk

# Ensure required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Path to store tweets
output_file = Path("scheduled_tweets.json")
today = datetime.utcnow().strftime("%Y-%m-%d")

# Avoid regenerating for the same day
if output_file.exists():
    try:
        existing = json.load(output_file.open())
        if existing.get("date") == today:
            print("✅ Tweets already generated for today.")
            exit(0)
    except json.JSONDecodeError:
        print("⚠️ Corrupted JSON file. Will overwrite.")

# Prompt for LLMs
prompt = f"""
You are a witty, up-to-date social media creator for X.com.
Your task is to:
1. Simulate searching Google News, Hacker News, X.com Trends, and TechCrunch.
2. Generate 10 distinct, scroll-stopping tweet options on recent trending tech/startup topics.
3. Use a variety of tones: insightful, funny, sarcastic, trending, and informative.

Each tweet should:
- Be ≤280 characters
- Be 4–6 sentences when possible
- Include 2 smart hashtags
- Sound human, not robotic
- (Optional) Include meme or image idea

Format exactly like this:

---
Tweet 1:
[text] try to include space in text like
_________
_________

#hastags #hashtaags

if the post is humourous then
A:
B:
#humour # hashtag

#hashtags
Image suggestion: [desc]

Tweet 2:
...
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()
batch_size = 5  # Smaller batch size for free plan limits
num_batches = 20  # 20 batches * 5 tweets = 100 tweets, allowing for free tier request limits

# Try Gemini API first
raw_text = ""
try:
    import google.generativeai as genai

    gemini_key = os.getenv("GOOGLE_GEMINI")
    if not gemini_key:
        raise ValueError("Missing GOOGLE_GEMINI environment variable")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

except Exception as e:
    print("⚠️ Gemini failed:", e)

# Fallback to OpenAI if Gemini fails
if not 'model' in locals():
    try:
        import openai

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise Value Value("Missing OPENAI_API_KEY environment variable")

        openai.api_key = openai_key
    except Exception as e:
        print("❌ Both Gemini and OpenAI failed:", e)
        exit(1)

# Batch generation to respect free plan limits
for batch in range(num_batches):
    print(f"Generating batch {batch + 1}/{num_batches}...")
    try:
        if 'model' in locals():
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            print("✅ Gemini generation successful.")
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.choices[0].message.content.strip()
            print("✅ OpenAI generation successful.")

    except Exception as e:
        print("❌ LLM failed in batch {batch + 1}:", e)
        time.sleep(10)  # Delay for rate limits in free plan
        continue

    # Extract tweets using regex
    blocks = re.findall(
        r"Tweet \d+:\n(.*?)(?:\nImage suggestion:.*?)?(?=\nTweet \d+:|\Z)",
        raw_text,
        re.DOTALL
    )

    if not blocks:
        print("❌ Failed to parse tweets from response in batch {batch + 1}. Output was:\n")
        print(raw_text)
        continue

    # Use sentiment analysis to filter out negative/neutral tweets
    positive = [t.strip() for t in blocks if sia.polarity_scores(t)["compound"] > 0.0]  # Loosened to > 0.0 for more tweets

    # Add unique tweets
    for t in positive:
        if t not in seen and len(all_tweets) < 100:
            all_tweets.append(t)
            seen.add(t)

    # Delay to respect free plan rate limits
    time.sleep(5)

    # Stop if we have enough
    if len(all_tweets) >= 100:
        break

# Ensure ~100 tweets with fallback if needed
while len(all_tweets) < 100:
    fallback = get_llm_tweet()  # Assume fallback function from post_scheduled_tweet.py or simple default
    if fallback and fallback not in seen:
        all_tweets.append(fallback)
        seen.add(fallback)

# Save final output to JSON file
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:100]
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_tweets[:100])} tweets to '{output_file.name}'.")
except Exception as e:
    print("❌ Failed to save tweets:", e)
    exit(1)
