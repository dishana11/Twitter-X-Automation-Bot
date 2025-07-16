import os, json
from datetime import datetime
from pathlib import Path
from nltk.sentiment.vader import SentimentIntensityAnalyzer

output_file = Path("scheduled_tweets.json")
today = datetime.now().strftime("%Y-%m-%d")

# Prevent duplicate generation
if output_file.exists():
    try:
        existing = json.load(output_file.open())
        if existing.get("date") == today:
            print("✅ Already generated for today.")
            exit(0)
    except json.JSONDecodeError:
        print("⚠️ Corrupted JSON file. Overwriting.")

# Tweet generation prompt
prompt = '''You are a witty tech content creator...

(keep your existing prompt here)...
'''

tweets = []

# ✅ Try Gemini (correct usage)
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI"))
    model = genai.GenerativeModel("gemini-pro")  # <- fixed line
    response = model.generate_content(prompt)
    tweets = json.loads(response.text)
except Exception as e:
    print("⚠️ Gemini failed:", e)

# Fallback to OpenAI if Gemini fails and tweets are still empty
if not tweets:
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        tweets = json.loads(response.choices[0].message.content)
    except Exception as e:
        print("❌ OpenAI failed too:", e)
        exit(1)

# Filter for positivity
sia = SentimentIntensityAnalyzer()
positive = [t for t in tweets if sia.polarity_scores(t)["compound"] > 0.1][:5]

# Save to JSON file
with output_file.open("w") as f:
    json.dump({"date": today, "tweets": positive}, f)

print(f"✅ Generated and saved {len(positive)} positive tweets.")
