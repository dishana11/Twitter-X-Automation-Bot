import os, json
from datetime import datetime
from pathlib import Path
from nltk.sentiment.vader import SentimentIntensityAnalyzer

output_file = Path("scheduled_tweets.json")
today = datetime.now().strftime("%Y-%m-%d")
if output_file.exists():
    existing = json.load(output_file.open())
    if existing.get("date") == today:
        print("✅ Already generated for today.")
        exit(0)

prompt = '''
You are an extremely online, witty tech content creator who writes sharp, scroll-stopping tweets for a modern audience on X.com.

Your job:
➡️ Create 5 tweets per day.
➡️ Make sure they’re based on current trending topics, recent tech news, and startup buzz (past 3–5 days).
➡️ Prioritize positive or witty sentiment only.

Categories to include:
- 🚀 Trending product launches (e.g., Google, Tesla, Nvidia, Meta, OpenAI)
- 💸 Recent funding rounds (e.g., Scale AI, Y Combinator startups)
- 🎯 Career opportunities (e.g., internships, fellowships, hackathons)
- 😂 Developer humor and tech memes
- 🧠 AI breakthroughs (e.g., generative AI, new LLMs, AGI trends)

Each tweet must:
- Be 1 tweet long (max 280 characters)
- Be in natural, casual tone (avoid generic robotic phrases)
- Include 3 relevant hashtags
- Be unique and different from each other
- End with a newline if needed for readability

Output as a JSON list of 5 tweet strings (no numbering or formatting).
'''


try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt)
    tweets = json.loads(result.text)
except Exception as e:
    print("⚠️ Gemini failed, falling back to OpenAI:", e)
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    tweets = json.loads(response.choices[0].message.content)

sia = SentimentIntensityAnalyzer()
positive = [t for t in tweets if sia.polarity_scores(t)["compound"] > 0.1][:5]

with output_file.open("w") as f:
    json.dump({"date": today, "tweets": positive}, f)

print(f"✅ Generated and saved {len(positive)} positive tweets.")
