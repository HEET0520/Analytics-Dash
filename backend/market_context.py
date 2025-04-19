from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
if not NEWSAPI_KEY:
    raise ValueError("NEWSAPI_KEY not set. Get one from https://newsapi.org/register")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# Simple cache for news to avoid repeated API calls (saves resources)
_news_cache = {}
_cache_lifetime = 3600  # Cache news for 1 hour

def get_market_context(query="latest financial news"):
    """
    Fetch recent market news for context with caching.
    Args:
        query (str): News query string.
    Returns:
        str: Concatenated news titles.
    """
    current_time = time.time()
    
    # Check cache first
    if query in _news_cache:
        cache_time, cache_data = _news_cache[query]
        if current_time - cache_time < _cache_lifetime:
            return cache_data
    
    try:
        articles = newsapi.get_everything(q=query, language="en", page_size=5)
        context = "\n".join([article["title"] for article in articles["articles"]])
        result = context if context else "No recent market context available."
        
        # Update cache
        _news_cache[query] = (current_time, result)
        
        return result
    except Exception as e:
        print(f"Error fetching market news: {e}")
        return "Unable to fetch market context at this time."
