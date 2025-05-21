import os
import openai
import tweepy

# Load API keys from environment variables (matching your GitHub secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_CONSUMER_KEY = os.getenv("CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def generate_tweet():
    prompt = (
        "Write a catchy, interesting, and short tweet about the latest AI news or innovation, "
        "something that grabs attention and makes people curious."
    )
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,
        temperature=0.7,
        n=1,
        stop=None,
    )
    tweet = response.choices[0].text.strip()
    return tweet

def post_tweet(text):
    auth = tweepy.OAuth1UserHandler(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    api.update_status(text)
    print("Tweet posted:", text)

if __name__ == "__main__":
    tweet_text = generate_tweet()
    post_tweet(tweet_text)
