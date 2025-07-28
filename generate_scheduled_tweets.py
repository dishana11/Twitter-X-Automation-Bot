import os
import json
import re
from datetime import datetime
from pathlib import Path
import nltk

# Ensure required NLTK data is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Output path
output_file = Path("scheduled_tweets.json")
today = datetime.utcnow().strftime("%Y-%m-%d")

# Prevent duplicate generation
if output_file.exists():
    try:
        existing = json.load(output_file.open())
        if existing.get("date") == today:
            print("✅ Already generated for today.")
            exit(0)
    except json.JSONDecodeError:
        print("⚠️ Corrupted JSON file. Proceeding to overwrite.")

# Tweet generation prompt
prompt = f"""
You are a witty, up-to-date social media creator for X.com.
Your task is to:
1. Simulate searching Google News, Hacker News, X.com Trends, and TechCrunch.
2. Generate 5 distinct, scroll-stopping tweet options on recent trending tech/startup topics.
3. Use a variety of tones: insightful, funny, sarcastic, trending, and informative.

Each tweet should:
- Be ≤280 characters
- Be 4–6 sentences when possible
- Include 3–6 smart hashtags
- Sound human, not robotic
- (Optional) Include meme or image idea

Format exactly like this:

---
Tweet 1:
[text]

#hashtags
Image suggestion: [desc]

Tweet 2:
...
---
"""

# Try Gemini API first
raw_text = ""
try:
    import google.generativeai as genai

    gemini_key = os.getenv("GOOGLE_GEMINI")
    if not gemini_key:
        raise ValueError("Missing GOOGLE_GEMINI environment variable")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    print("✅ Gemini generation successful.")

except Exception as e:
    print("⚠️ Gemini failed:", e)

# Fallback: OpenAI
if not raw_text:
    try:
        import openai

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

        openai.api_key = openai_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content.strip()
        print("✅ OpenAI generation successful.")

    except Exception as e:
        print("❌ Both Gemini and OpenAI failed:", e)
        exit(1)

# Extract tweets from the raw output
blocks = re.findall(
    r"Tweet \d+:\n(.+?)\n\n#.*?\nImage suggestion:.*",
    raw_text,
    re.DOTALL
)

if not blocks:
    print("❌ Failed to parse tweets. Raw output:")
    print(raw_text)
    exit(1)

# Filter by sentiment
sia = SentimentIntensityAnalyzer()
positive = [t.strip() for t in blocks if sia.polarity_scores(t)["compound"] > 0.1][:5]

if not positive:
    print("⚠️ No positive tweets found.")
    exit(1)

# Save to JSON
try:
    with output_file.open("w") as f:
        json.dump({"date": today, "tweets": positive}, f, indent=2)
    print(f"✅ Saved {len(positive)} tweets to '{output_file.name}'.")
except Exception as e:
    print("❌ Failed to save file:", e)
