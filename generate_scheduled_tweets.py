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
prompt = """
You are a witty, casual social media creator who writes posts for platforms like X.com (Twitter) and LinkedIn. Your posts should be:
- Mostly short, punchy, and humorous one-liners or quick observations.
- But also include some longer, paragraph-style posts with jokes, commentary, or stories.
- Use a natural mix of topics: technology, AI, physics, history, startup/industry news, and fun trivia.
- Hashtags are optional. If used, include 1 or 2 hashtags with proper spacing (e.g., "#Tech #Innovation") within the post text.
- Sometimes include playful or clever wording.
- Posts should feel human, like a smart friend chatting casually, not robotic or formal.
- Some posts can start with "Did you know?" or pose a fun question.
- Include image suggestions for approximately 20% of posts (e.g., 1 in every 5 posts), formatted as:
  Image suggestion: [describe the image clearly, suitable for generating a visual with AI tools like DALL-E]

Format your output exactly like this, numbering posts sequentially:

---
Post 1:
Grok works nice. #AI #Tech

Post 2:
Jekyll on GitHub is so cool.

Post 3:
Did you know? The first computer bug was an actual moth.

Post 4:
TechCrunch says the foldable phone is back. But is it back-back? Like, can it survive a drop from my pocket without shattering into a million pieces? The jury's still out. #FoldablePhones #TechFail
Image suggestion: A cartoon of a foldable phone snapping in half.

Post 5:
Saw on Google News that someone paid millions for an NFT of a pixelated rock. I just picked one up from my backyard for free. Anyone want to make me an offer? #NFTMadness #RockSolidInvestment
Image suggestion: A picture of a regular rock next to a pixelated rock NFT.
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()
batch_size = 5  # 5 tweets per batch
num_batches = 25  # Increased to ensure ~100 tweets after filtering

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
except Exception as e:
    print(f"⚠️ Gemini setup failed: {e}")

# Fallback to OpenAI if Gemini fails
if 'model' not in locals():
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
    except Exception as e:
        print(f"❌ Both Gemini and OpenAI setup failed: {e}")
        exit(1)

# Batch generation to respect free plan limits
for batch in range(num_batches):
    print(f"Generating batch {batch + 1}/{num_batches}...")
    try:
        if 'model' in locals():
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            print(f"✅ Gemini batch {batch + 1} successful.")
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            raw_text = response.choices[0].message.content.strip()
            print(f"✅ OpenAI batch {batch + 1} successful.")
    except Exception as e:
        print(f"❌ Batch {batch + 1} failed: {e}")
        time.sleep(10)  # Delay for rate limits
        continue

    # Log raw response for debugging
    with open("raw_response_log.txt", "a", encoding="utf-8") as f:
        f.write(f"Batch {batch + 1} response:\n{raw_text}\n\n")

    # Extract posts and image suggestions
    pattern = re.compile(
        r"Post \d+:\n(.*?)(?:\nImage suggestion: (.*?))?(?=\nPost \d+:|\Z)",
        re.DOTALL
    )
    matches = pattern.findall(raw_text)

    if not matches:
        print(f"❌ Failed to parse posts in batch {batch + 1}. Output was:\n{raw_text}")
        continue

    # Filter tweets
    for text, image_suggestion in matches:
        text = text.strip()
        image_suggestion = image_suggestion.strip() if image_suggestion else None
        if (len(text) <= 280 and
            text not in seen and
            sia.polarity_scores(text)["compound"] > 0.1):
            all_tweets.append({"text": text, "image_suggestion": image_suggestion})
            seen.add(text)

    # Stop if we have enough
    if len(all_tweets) >= 100:
        break

    # Delay to respect free plan rate limits
    time.sleep(5)

# Warn if fewer than 100 tweets
if len(all_tweets) < 100:
    print(f"⚠️ Generated only {len(all_tweets)} tweets, less than 100. Saving anyway.")

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:100]
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_tweets[:100])} tweets to '{output_file.name}'.")
except Exception as e:
    print(f"❌ Failed to save tweets: {e}")
    exit(1)
