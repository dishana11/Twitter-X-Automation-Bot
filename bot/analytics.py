import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    def __init__(self):
        self.daily_stats = {}
        logger.info("AnalyticsTracker initialized")

    def get_daily_stats(self, date_str):
        """
        Return stats for the given date as a dictionary.
        If there are no stats yet, return an empty dict.
        """
        return self.daily_stats.get(date_str, {})

    def record_tweet(self, tweet_id, content, tweet_type="intelligent_v2"):
        date_str = datetime.now().date().isoformat()
        if date_str not in self.daily_stats:
            self.daily_stats[date_str] = {"tweets_posted": 0, "tweets": []}
        self.daily_stats[date_str]["tweets_posted"] += 1
        self.daily_stats[date_str]["tweets"].append({
            "id": tweet_id,
            "content": content,
            "type": tweet_type,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Recorded tweet: {tweet_id}")
