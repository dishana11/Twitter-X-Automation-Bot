import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
import nltk
from tenacity import retry, stop_after_attempt, wait_fixed

# Ensure required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Path to store tweets
output_file = Path("scheduled_tweets.json")
log_file = Path("tweet_gen_log.txt")
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
[text]
#hashtag1 #hashtag2
Image suggestion: [desc]

Tweet 2:
...
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()
batch_size = 10
num_batches = 12  # Allow extra batches for failures

# Validate environment variables
required_env = ["GOOGLE_GEMINI", "OPENAI_API_KEY"]
for env in required_env:
    if not os.getenv(env):
        print(f"❌ Missing environment variable: {env}")
        with open(log_file, "a") as f:
            f.write(f"{datetime.utcnow()}: Missing env var {env}\n")
        exit(1)

# Retry decorator for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def call_gemini(prompt):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def call_openai(prompt):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )
    return response.choices[0].message.content.strip()

# Batch generation
for batch in range(num_batches):
    print(f"Generating batch {batch + 1}/{num_batches}...")
    raw_text = ""
    
    # Try Gemini API first
    try:
        raw_text = call_gemini(prompt)
        print(f"✅ Gemini batch {batch + 1} successful.")
        with open(log_file, "a") as f:
            f.write(f"{datetime.utcnow()}: Gemini batch {batch + 1} success\n")
    except Exception as e:
        print(f"⚠️ Gemini batch {batch + 1} failed: {e}")
        with open(log_file, "a") as f:
            f.write(f"{datetime.utcnow()}: Gemini batch {batch + 1} failed: {e}\n")

    # Fallback to OpenAI
    if not raw_text:
        try:
            raw_text = call_openai(prompt)
            print(f"✅ OpenAI batch {batch + 1} successful.")
            with open(log_file, "a") as f:
                f.write(f"{datetime.utcnow()}: OpenAI batch {batch + 1} success\n")
        except Exception as e:
            print(f"❌ OpenAI batch {batch + 1} failed: {e}")
            with open(log_file, "a") as f:
                f.write(f"{datetime.utcnow()}: OpenAI batch {batch + 1} failed: {e}\n")
            continue

    # Extract tweets with robust regex
    blocks = re.findall(
        r"Tweet \d+:\n\s*(.*?)(?=\n\s*Tweet \d+:|\Z)",
        raw_text,
        re.DOTALL
    )

    if not blocks:
        print(f"❌ Failed to parse tweets in batch {batch + 1}. Skipping.")
        with open(log_file, "a") as f:
            f.write(f"{datetime.utcnow()}: Failed to parse batch {batch + 1}\n")
        continue

    # Filter tweets
    for t in blocks:
        tweet_text = t.strip()
        if len(tweet_text) <= 280 and tweet_text not in seen and sia.polarity_scores(tweet_text)["compound"] > 0.0:
            all_tweets.append(tweet_text)
            seen.add(tweet_text)

    # Stop early if we have enough tweets
    if len(all_tweets) >= 100:
        break

    # Avoid rate limits
    if batch < num_batches - 1:
        time.sleep(5)

# Limit to 100 tweets
tweets = all_tweets[:100]
print(f"📝 Total unique positive tweets generated: {len(tweets)}")
with open(log_file, "a") as f:
    f.write(f"{datetime.utcnow()}: Generated {len(tweets)} tweets\n")

if len(tweets) < 100:
    print(f"⚠️ Only {len(tweets)} positive, unique tweets generated. Consider loosening sentiment threshold or increasing batches.")
    with open(log_file, "a") as f:
        f.write(f"{datetime.utcnow()}: Warning: Only {len(tweets)} tweets generated\n")

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": tweets
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(tweets)} tweets to '{output_file.name}'.")
    with open(log_file, "a") as f:
        f.write(f"{datetime.utcnow()}: Saved {len(tweets)} tweets to {output_file.name}\n")
except Exception as e:
    print(f"❌ Failed to save tweets: {e}")
    with open(log_file, "a") as f:
        f.write(f"{datetime.utcnow()}: Failed to save tweets: {e}\n")
    exit(1)
