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
  - Example: "Found a data science internship at Google! They need undergrads to analyze datasets with Python. It’s a 12-week program with expert mentors. What they want: → Python skills → Data curiosity → Team players. Degrees get you noticed; projects get you hired. Ready to code?"
- 9 posts: Focus on freelancing, job hunting, skills vs degrees, developer growth, reality checks, or income growth. Use arrow-driven, contrast-heavy style with fresh angles. No links or images.
  - Example: "Most job seekers fail. They apply → 100 jobs → Generic CVs → No follow-up. Winners do: → Target 10 roles → Build portfolios → Network smartly. Applications don’t win; proof does. How will you show your impact?"

Format output exactly like this, numbering posts sequentially:
---
Post 1:
[text]

Post 2:
[text]

Post 3:
[text]
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
num_batches = 4  # 4 batches * 5 tweets = 20 tweets

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
        if (len(tweet_text) >= 500 and
            len(tweet_text) <= 600 and
            tweet_text not in seen and
            sia.polarity_scores(tweet_text)["compound"] > 0.1):
            all_tweets.append({"text": tweet_text})
            seen.add(tweet_text)

    # Stop if we have enough
    if len(all_tweets) >= 20:
        break

    # Delay to respect free plan rate limits
    time.sleep(5)

# Fallback tweets if <20
default_tweets = [
    "Spotted a machine learning internship at NVIDIA! They need undergrads for GPU-accelerated AI projects. It’s a 12-week program with hands-on coding. What they seek: → Python skills → Problem-solving grit → Team synergy. Degrees open doors; projects seal the deal. Ready to build AI?",
    "Most freelancers stay broke. They chase → Low-paying gigs → One-off clients → Endless revisions. Winners do: → Niche down → Charge premium → Build repeat business. Cheap work costs you time. High-value work builds wealth. What’s your next client move?",
    "Job seekers get ignored in 2025. They focus → Certificates → Generic CVs → Mass applications. Success demands: → Portfolios → Targeted outreach → Proof of impact. Resumes tell; projects show. How will you prove you’re the one to hire?"
]
while len(all_tweets) < 20:
    fallback = default_tweets[len(all_tweets) % len(default_tweets)]
    if fallback not in seen and len(fallback) >= 500 and len(fallback) <= 600:
        all_tweets.append({"text": fallback})
        seen.add(fallback)

# Save to JSON
try:
    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "tweets": all_tweets[:20]
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_tweets[:20])} tweets to '{output_file.name}'.")
except Exception as e:
    print(f"❌ Failed to save tweets: {e}")
    exit(1)
