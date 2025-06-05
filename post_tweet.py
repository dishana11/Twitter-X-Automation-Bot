import os
import tweepy
from bot.sentiment_analyzer import SentimentAnalyzer
from config.settings import get_api_credentials

def main():
    content = os.getenv('TWEET_CONTENT', '')
    force = os.getenv('FORCE_POST', 'false').lower() == 'true'
    
    sentiment_analyzer = SentimentAnalyzer()
    credentials = get_api_credentials()
    client = tweepy.Client(
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

    sentiment_result = sentiment_analyzer.analyze_sentiment(content)
    print(f'Content: {content}')
    print(f"Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']:.3f})")

    should_post = force or sentiment_result['sentiment'] != 'negative' or sentiment_result['confidence'] < 0.5

    if should_post:
        try:
            response = client.create_tweet(text=content)
            tweet_id = response.data['id']
            print(f'Tweet posted successfully! ID: {tweet_id}')
            print(f'URL: https://twitter.com/i/web/status/{tweet_id}')
        except Exception as e:
            print(f'Failed to post: {e}')
            exit(1)
    else:
        print('Tweet not posted due to negative sentiment. Use force_post=true to override.')
        exit(1)

if __name__ == '__main__':
    main()
