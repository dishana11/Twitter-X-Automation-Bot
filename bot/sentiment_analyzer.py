
"""
Sentiment Analysis Module
Provides sentiment analysis functionality using VADER and TextBlob
"""

import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analyzer with VADER and TextBlob"""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        logger.info("Sentiment analyzer initialized")
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment using both VADER and TextBlob
        Returns sentiment classification and confidence score
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'vader_scores': {},
                'textblob_polarity': 0.0
            }
        
        # VADER Analysis
        vader_scores = self.vader_analyzer.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob Analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combined analysis
        combined_score = (vader_compound + textblob_polarity) / 2
        
        # Determine sentiment
        if combined_score >= 0.1:
            sentiment = 'positive'
        elif combined_score <= -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence (absolute value of combined score)
        confidence = abs(combined_score)
        
        result = {
            'sentiment': sentiment,
            'confidence': confidence,
            'vader_scores': vader_scores,
            'textblob_polarity': textblob_polarity,
            'combined_score': combined_score
        }
        
        logger.info(f"Sentiment analysis result: {sentiment} (confidence: {confidence:.3f})")
        return result
    
    def is_positive(self, text, threshold=0.1):
        """Check if text has positive sentiment above threshold"""
        result = self.analyze_sentiment(text)
        return result['sentiment'] == 'positive' and result['confidence'] >= threshold
    
    def is_negative(self, text, threshold=0.1):
        """Check if text has negative sentiment above threshold"""
        result = self.analyze_sentiment(text)
        return result['sentiment'] == 'negative' and result['confidence'] >= threshold
