from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

def get_market_context(query="latest financial news"):
    """
    Fetch recent market news for context.
    Args:
        query (str): News query string.
    Returns:
        str: Concatenated news titles.
    """
    articles = newsapi.get_everything(q=query, language="en", page_size=5)
    context = "\n".join([article["title"] for article in articles["articles"]])
    return context if context else "No recent market context available."