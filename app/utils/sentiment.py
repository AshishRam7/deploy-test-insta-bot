# app/utils/sentiment.py
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import logging

logger = logging.getLogger(__name__)

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def analyze_sentiment(comment_text):
    """Analyzes sentiment of text using NLTK's VADER."""
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(comment_text)
    if sentiment_scores['compound'] > 0.25:
        sentiment = "Positive"
    else:
        sentiment = "Negative"  # Consider neutral as negative for default responses
    return sentiment