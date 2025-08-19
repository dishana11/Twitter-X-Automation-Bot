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
log_file = Path("tweet_post_log.txt")
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
You are a witty, casual social media creator who writes posts for platforms like X.com and LinkedIn. Your posts must be unique, engaging, and high-quality, ensuring they do not repeat content previously posted (avoid duplicating ideas or phrasing from past posts). Generate exactly 24 posts per day, with the following requirements:

- **14 posts/day**: Focus on new intern positions, research positions, career programs, or career internships. Simulate searching job boards, company career pages, and academic sites to find opportunities. Posts must be:
  - Longer than 280 characters, well-paragraphed (2-3 short paragraphs).
  - Accurate, professional, and informative (e.g., mention company names like NVIDIA, DeepMind, or others, fields like tech/AI, or program details without links).
  - Include 1-2 relevant hashtags in the text (e.g., "#Internships #TechCareers").
  - No links or image suggestions.
  - Example: "Just found an awesome AI research internship at DeepMind! They’re looking for undergrads with Python skills to work on cutting-edge NLP projects. It’s a 6-month program with mentorship from top researchers. Perfect for anyone wanting to dive into AI! #AIInternships #TechCareers"

- **10 posts/day**: Creative, witty posts about tech, AI, or career advice, styled like these examples:
  - Example 1: "If you could pick one dev superpower: a) bug-free code first try, b) instant codebase mastery, c) perfect 6-hour workdays, d) auto-negotiated top salaries. What’s your choice? I’m torn between b and c! #TechLife #CareerAdvice"
  - Example 2: "Your degree gets the interview. Your GitHub gets the callback. Your communication seals the offer. Your learning keeps you promoted. Most stop at step 1. Keep pushing! #CareerGrowth #TechCareers"
  - Example 3: "AI models like Kling are getting too ‘human’—collapsing complex ideas into mainstream takes. I asked about burnout and it spat back ‘chronic fatigue.’ Nope, not the same. Let’s keep AI open-minded for real insights! #AI #TechInsights"
  - Posts can be lists, questions, or critiques of AI trends (e.g., models like Kling, VEO, or o3 being overly mainstream or lazy). Longer than 280 characters, 1-2 hashtags in text, no links or image suggestions.

- Posts should feel human, like a smart friend chatting casually, not robotic or formal.
- Some posts can start with "Did you know?" or pose a fun question.
- Ensure variety in topics (tech, AI, physics, history, startups, trivia) and avoid repeating ideas or phrasing from past posts.

Format your output exactly like this, numbering posts sequentially:
---
Post 1:
[text with hashtags]

Post 2:
[text with hashtags]

Post 3:
[text with hashtags]
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()

# Load previously posted tweets from tweet_post_log.txt to avoid repeats
if log_file.exists():
    try:
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                if "Posted tweet:" in line:
                    tweet_text = line.split("Posted tweet:")[1].split("(ID:")[0].strip()
                    seen.add(tweet_text)
    except Exception as e:
        print(f"⚠️ Error reading tweet_post_log.txt: {e}")

batch_size = 5  # Smaller batch size for free plan limits
num_batches = 5  # 5 batches * 5 tweets = 25 tweets, trimmed to 24

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

    # Extract tweets
    pattern = re.compile(r"Post \d+:\n(.*?)(?=\nPost \d+:|\Z)", re.DOTALL)
    matches = pattern.findall(raw_text)

    if not matches:
        print(f"❌ Failed to parse posts in batch {batch + 1}. Output was:\n{raw_text}")
        continue

    # Filter tweets
    for tweet_text in matches:
        tweet_text = tweet_text.strip()
        if (len(tweet_text) > 280 and
            tweet_text not in seen and
            sia.polarity_scores(tweet_text)["compound"] > 0.1):
            all_tweets.append({"text": tweet_text})
            seen.add(tweet_text)

    # Stop if we have enough
    if len(all_tweets) >= 24:
        break

    # Delay to respect free plan rate limits
    time.sleep(5)

# Fallback tweets if <24
default_tweets = [
    "Just spotted a machine learning internship at NVIDIA! They’re seeking students to work on GPU-accelerated AI models. It’s a 12-week program with hands-on projects in deep learning. Time to polish your Python skills and apply! #AIInternships #TechCareers",
    "Your portfolio gets you noticed. Your projects get you interviewed. Your passion gets you hired. Your growth keeps you thriving. Don’t stop at a degree—build something real! #CareerGrowth #TechCareers",
    "AI models like VEO are getting too mainstream, collapsing complex ideas into safe answers. I asked about career paths, and it suggested ‘get a CS degree.’ Nah, build real projects and stand out! #AI #TechInsights"
]
while len(all_tweets) < 24:
    fallback = default_tweets[len(all_tweets) % len(default_tweets)]
    if fallback not in seen:
        all_tweets.append({"text": fallback})
        seen.add(fallback)

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:24]
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_tweets[:24])} tweets to '{output_file.name}'.")
except Exception as e:
    print(f"❌ Failed to save tweets: {e}")
    exit(1)
