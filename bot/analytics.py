import logging

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    def __init__(self):
        """Initialize your analytics tracker (e.g., set up files, APIs, etc.)"""
        logger.info("AnalyticsTracker initialized")

    def track(self, event_name, data=None):
        """
        Track an event with optional data.
        :param event_name: Name of the event (str)
        :param data: Additional data (dict or None)
        """
        if data is None:
            data = {}
        logger.info(f"Tracked event: {event_name} | Data: {data}")
        # Here you could send the data to a database, analytics service, or write to a file
