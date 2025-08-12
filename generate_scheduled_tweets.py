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
- Mostly short, punchy, and humorous one-liners or quick observations.Don't include the prompt in the post only content and then hashtag with two line gap after content this is mandatory 
- But also include some longer, paragraph-style posts with jokes, commentary, or stories.
- Use a natural mix of topics: technology, AI, physics, history, startup/industry news, and fun trivia.
- Hashtags are optional. If used, include 1 or 2 hashtags with proper spacing (e.g., "#Tech #Innovation").
- Sometimes include playful or clever wording.
- Posts should feel human, like a smart friend chatting casually, not robotic or formal.
- Some posts can start with "Did you know?" or pose a fun question.


Format your output exactly like this, numbering posts sequentially:
---
Post 1:
[text]
leave two line gap then
#hashtag1 #hashtag2


Post 2:
[text]
leave a line gap
#hashtag

Post 3:
[text]

---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()
batch_size = 5  # Smaller batch size for free plan limits
num_batches = 20  # 20 batches * 5 tweets = 100 tweets

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

    # Extract tweets and image suggestions
    pattern = re.compile(
        r"Post \d+:\n((?:.*?\n)*?)(?:(?:\nImage suggestion: (.*?))?)(?=\nPost \d+:|\Z)",
        re.DOTALL
    )
    matches = pattern.findall(raw_text)

    if not matches:
        print(f"❌ Failed to parse posts in batch {batch + 1}. Output was:\n{raw_text}")
        continue

    # Filter tweets
    for post_text, image_suggestion in matches:
        tweet_text = post_text.strip()
        if len(tweet_text) <= 280 and tweet_text not in seen and sia.polarity_scores(tweet_text)["compound"] > 0.1:
            all_tweets.append({"text": tweet_text, "image_suggestion": image_suggestion or None})
            seen.add(tweet_text)

    # Stop if enough tweets
    if len(all_tweets) >= 100:
        break

    # Delay to respect free plan rate limits
    time.sleep(5)

# Fallback tweets if <100
default_tweets = [
    "AI is transforming tech daily! What's the next big thing? #AI #Innovation",
    "Startups are pushing boundaries. What's your favorite tool? #Startups #TechTrends",
    "Coding is the new superpower! Ready to build the future? #Coding #Tech",
    "Tech moves fast—stay ahead with the latest tools! #Innovation #Startups"
]
while len(all_tweets) < 100:
    fallback = default_tweets[len(all_tweets) % len(default_tweets)]
    if fallback not in seen:
        all_tweets.append({"text": fallback, "image_suggestion": None})
        seen.add(fallback)

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
