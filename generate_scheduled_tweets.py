# generate_scheduled_tweets.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
Generate 5 funny, sarcastic, or witty tech-related tweets with an optional image suggestion.
Each tweet should start with 'Tweet 1:', 'Tweet 2:', etc., and include:
1. The tweet content (max 280 characters).
2. An image suggestion (optional, start line with "Image suggestion:").

Do not include extra text or explanations. Format:
Tweet 1:
your tweet

Image suggestion: your image idea

Tweet 2:
...
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.9,
)

output = response.choices[0].message.content.strip()
print("✅ Gemini generation successful.\n")

tweets = output.split("Tweet ")[1:]

if not tweets:
    print("❌ Failed to parse tweets from response. Output was:\n\n", output)
    exit(1)

with open("scheduled_tweets.txt", "w", encoding="utf-8") as f:
    for tweet in tweets:
        try:
            number, content = tweet.split(":", 1)
            content_parts = content.strip().split("Image suggestion:")
            tweet_text = content_parts[0].strip()
            image_text = content_parts[1].strip() if len(content_parts) > 1 else None

            f.write("---TWEET---\n")
            f.write(f"Tweet: {tweet_text}\n")
            if image_text:
                f.write(f"Image: {image_text}\n")
            f.write("---END---\n\n")
        except Exception as e:
            print(f"⚠️ Error parsing a tweet block:\n{tweet}\n{e}\n")

print("✅ Tweets saved to scheduled_tweets.txt")
