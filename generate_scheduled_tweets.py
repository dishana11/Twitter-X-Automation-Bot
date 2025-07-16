import os, json
from datetime import datetime
from pathlib import Path
from nltk.sentiment.vader import SentimentIntensityAnalyzer

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
        print("⚠️ Corrupted JSON file. Overwriting.")

# Prompt for Gemini/OpenAI
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

# Use Gemini first
raw_text = ""
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    raw_text = response.text
except Exception as e:
    print("⚠️ Gemini failed:", e)

# Fallback to OpenAI
if not raw_text:
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content
    except Exception as e:
        print("❌ OpenAI failed too:", e)
        exit(1)

# Extract tweet text blocks
import re
blocks = re.findall(r"Tweet \d+:\n(.+?)\n\n#.*?\nImage suggestion:.*", raw_text, re.DOTALL)

if not blocks:
    print("❌ Failed to parse tweets.")
    exit(1)

# Sentiment filter
sia = SentimentIntensityAnalyzer()
positive = [t.strip() for t in blocks if sia.polarity_scores(t)["compound"] > 0.1][:5]

# Save
with output_file.open("w") as f:
    json.dump({"date": today, "tweets": positive}, f)

print(f"✅ Saved {len(positive)} tweets.")
