```python
import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
import nltk
import logging
import requests

# Set up logging
logging.basicConfig(filename='tweet_gen_log.txt', level=logging.INFO, 
                    format='%(asctime)s: %(message)s')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Paths
output_file = Path("scheduled_tweets.json")
log_file = Path("tweet_post_log.txt")
today = datetime.utcnow().strftime("%Y-%m-%d")

# Avoid regenerating for the same day
if output_file.exists():
    try:
        with output_file.open('r', encoding='utf-8') as f:
            existing = json.load(f)
        if existing.get("date") == today and len(existing.get("tweets", [])) >= 20:
            logging.info("Tweets already generated for today.")
            print("✅ Tweets already generated for today.")
            exit(0)
    except json.JSONDecodeError:
        logging.warning("Corrupted JSON file. Will overwrite.")
        print("⚠️ Corrupted JSON file. Will overwrite.")

# Prompt for LLMs
prompt = """
Write 20 long-form tweets for Twitter/X. Each tweet must be 500–600 characters. Posts must be unique, avoiding repeated ideas, phrasing, or headings from past posts (e.g., no “10x dev” or “degree won’t save you”). Check against previous posts to ensure originality.

Writing Style Rules:
- Use short, direct sentences. Break lines often for rhythm and impact.
- Use arrows (→) to show flow, outcomes, or contrasts (e.g., Skills → Projects → Clients → Money).
- Use contrasts like Results > Certificates, Portfolio > Resume, Execution > Theory.
- Each tweet should: Share a framework (steps to achieve something), OR Deliver a reality check (bold truth people ignore), OR End with a question to spark engagement.
- No emojis, no hashtags, no fluff. Keep it sharp, confident, and thought-leadership style.

Structure Each Tweet:
- Hook/Statement: Bold opening line to grab attention.
- Breakdown with Arrows: Short phrases separated by arrows or line breaks.
- Contrast: What people think vs what actually works.
- Engagement Question or Punchline: Something that leaves the reader thinking.

Topics to Cover:
- Freelancing: Client psychology, scaling, mistakes, positioning, earning first 1 lakh, upgrading clients.
- Job Hunting: Getting hired faster, referrals, portfolios vs resumes, recruiter mindset, common mistakes.
- Skills vs Degrees: What matters in 2025+, why degrees alone won’t save you, how proof of work beats certificates.
- Developer Growth: Becoming a high-impact dev, automation mindset, writing maintainable code, solving business problems.
- Reality Checks: Why people stay stuck, why freelancers stay broke, why job seekers get ignored, why clients undervalue you.
- Income Growth: Moving from low-paying to premium clients, earning more than Tier 1 grads, stacking skills for leverage.

Generate exactly 20 posts per day:
- 11 posts: Focus on new intern positions, research positions, career programs, or career internships. Simulate searching job boards, company career pages, and academic sites. Include company names (e.g., NVIDIA, DeepMind), fields (e.g., tech/AI), or program details without links. Use arrow-driven, contrast-heavy style. No links or images.
- 9 posts: Focus on freelancing, job hunting, skills vs degrees, developer growth, reality checks, or income growth. Use arrow-driven, contrast-heavy style with fresh angles. No links or images.

Format output exactly like this:
---
Post 1:
[text]

Post 2:
[text]

...
Post 20:
[text]
---
"""

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()
all_tweets = []
seen = set()

# Optimize duplicate checking
def check_duplicate(tweet, log_file=log_file, max_lines=1000):
    """Check if tweet is a duplicate, reading only recent lines."""
    if not log_file.exists():
        return False
    try:
        with log_file.open('r', encoding='utf-8') as f:
            lines = f.readlines()[-max_lines:]  # Read last 1000 lines
        return any(tweet in line for line in lines if "Posted tweet:" in line)
    except Exception as e:
        logging.error(f"Error reading tweet_post_log.txt: {e}")
        return False

# Load seen tweets
if log_file.exists():
    try:
        with log_file.open('r', encoding='utf-8') as f:
            lines = f.readlines()[-1000:]  # Limit to recent entries
        for line in lines:
            if "Posted tweet:" in line:
                tweet_text = line.split("Posted tweet:")[1].split("(ID:")[0].strip()
                seen.add(tweet_text)
    except Exception as e:
        logging.error(f"Error reading tweet_post_log.txt: {e}")

# Validate environment variables
required_env = ["GOOGLE_GEMINI", "OPENAI_API_KEY"]
for env in required_env:
    if not os.getenv(env):
        logging.error(f"Missing environment variable: {env}")
        print(f"❌ Missing environment variable: {env}")
        exit(1)

# Try Gemini API first
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
except Exception as e:
    logging.warning(f"Gemini setup failed: {e}")
    print(f"⚠️ Gemini setup failed: {e}")

# Fallback to OpenAI
if 'model' not in locals():
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Missing OPENAI_API_KEY")
    except Exception as e:
        logging.error(f"Both Gemini and OpenAI setup failed: {e}")
        print(f"❌ Both Gemini and OpenAI setup failed: {e}")
        exit(1)

# Batch generation
batch_size = 4  # 4 tweets per batch
num_batches = 5  # 5 batches * 4 = 20 tweets
for batch in range(num_batches):
    batch_prompt = prompt.replace("Write 20 long-form tweets", f"Write {batch_size} long-form tweets")
    logging.info(f"Generating batch {batch + 1}/{num_batches}...")
    print(f"Generating batch {batch + 1}/{num_batches}...")
    try:
        start_time = time.time()
        if 'model' in locals():
            response = model.generate_content(batch_prompt, request_options={"timeout": 30})
            raw_text = response.text.strip()
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": batch_prompt}],
                max_tokens=1200,
                timeout=30
            )
            raw_text = response.choices[0].message.content.strip()
        logging.info(f"Batch {batch + 1} generated in {time.time() - start_time:.2f}s")
        print(f"✅ Batch {batch + 1} successful.")
    except Exception as e:
        logging.error(f"Batch {batch + 1} failed: {e}")
        print(f"❌ Batch {batch + 1} failed: {e}")
        time.sleep(2 ** min(batch, 5))  # Exponential backoff
        continue

    # Log raw response
    with open("raw_response_log.txt", "a", encoding="utf-8") as f:
        f.write(f"Batch {batch + 1} response:\n{raw_text}\n\n")

    # Extract tweets
    pattern = re.compile(r"Post \d+:\n(.*?)(?=\nPost \d+:|\Z)", re.DOTALL)
    matches = pattern.findall(raw_text)
    if not matches:
        logging.error(f"Failed to parse posts in batch {batch + 1}. Output: {raw_text}")
        print(f"❌ Failed to parse posts in batch {batch + 1}.")
        continue

    for tweet_text in matches:
        tweet_text = tweet_text.strip()
        if (500 <= len(tweet_text) <= 600 and
            not check_duplicate(tweet_text) and
            sia.polarity_scores(tweet_text)["compound"] > 0.1):
            all_tweets.append({"text": tweet_text})
            seen.add(tweet_text)

    if len(all_tweets) >= 20:
        break
    time.sleep(5)  # Rate limit delay

# Fallback tweets
default_tweets = [
    "Found an AI research internship at DeepMind! They seek grads for NLP projects. It’s a 6-month program with cutting-edge mentors. Path to impact: → Learn PyTorch → Build prototypes → Publish findings. Degrees get you in; research wins the game. Ready to shape AI’s future?",
    "Freelancers plateau fast. They grind → Low-value gigs → No systems → Burnout. Pros do: → Specialize → Automate tasks → Upsell retainers. Chasing clients wastes time; systems build wealth. What’s your next step to scale?",
    "Job seekers lose in 2025. They spam → Resumes → Generic skills → No network. Winners focus: → Portfolios → Referrals → Business impact. Applications fade; proof shines. How will you stand out in a crowded market?"
]
while len(all_tweets) < 20:
    fallback = default_tweets[len(all_tweets) % len(default_tweets)]
    if not check_duplicate(fallback) and 500 <= len(fallback) <= 600:
        all_tweets.append({"text": fallback})
        seen.add(fallback)

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:20]
        }, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {len(all_tweets[:20])} tweets to {output_file.name}")
    print(f"✅ Saved {len(all_tweets[:20])} tweets to '{output_file.name}'.")
except Exception as e:
    logging.error(f"Failed to save tweets: {e}")
    print(f"❌ Failed to save tweets: {e}")
    exit(1)
```
