import os
import requests
from groq import Groq
from dotenv import load_dotenv
from cachetools import TTLCache
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

class MarketContextAgent:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
        logger.info(f"NewsAPI key loaded: {'Yes' if self.newsapi_key else 'No'}")
        logger.info(f"Groq API key loaded: {'Yes' if groq_api_key else 'No'}")
        if not all([self.groq_client, self.newsapi_key]):
            raise ValueError("Missing API keys in .env file")
        self.cache = TTLCache(maxsize=100, ttl=3600)

    def get_market_context(self, ticker, retries=3):
        logger.info(f"Fetching market context for {ticker}")
        cache_key = f"news_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached market context for {ticker}")
            return self.cache[cache_key]

        news = self.fetch_news(ticker, retries)
        if isinstance(news, str):
            return news

        # Build news summary string outside f-string to avoid backslash issues
        news_summary = "".join([f"- {article['title']} ({article['description']})\n" for article in news[:5]])
        prompt = (
            f"Summarize the market sentiment for {ticker} based on the following news articles:\n"
            f"{news_summary}"
            "Provide a concise summary (100-150 words) focusing on sentiment, key events, and their potential impact on the stock."
        )
        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=200
                )
                context = response.choices[0].message.content
                self.cache[cache_key] = context
                logger.info(f"Market context generated for {ticker}")
                return context
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return "Error generating market context."

    def fetch_news(self, ticker, retries=3):
        for attempt in range(retries):
            try:
                url = (
                    f"https://newsapi.org/v2/everything?q={ticker}+stock&language=en&sortBy=publishedAt"
                    f"&apiKey={self.newsapi_key}"
                )
                response = requests.get(url)
                response.raise_for_status()
                articles = response.json().get("articles", [])
                if not articles:
                    logger.info(f"No news articles found for {ticker}")
                    return "No recent news found."
                news = [
                    {
                        "title": article["title"] or "No title available",
                        "source": article["source"]["name"] or "Unknown source",
                        "published_at": article["publishedAt"] or "Unknown date",
                        "description": article["description"] or "No description available",
                        "url": article["url"] or "#"
                    }
                    for article in articles[:5]
                ]
                logger.info(f"Fetched {len(news)} news articles for {ticker}")
                return news
            except requests.exceptions.HTTPError as e:
                logger.error(f"News fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"News fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"Error fetching news for {ticker} after {retries} attempts")
        return f"Error fetching news for {ticker} after {retries} attempts."