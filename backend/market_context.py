import os
import re
import time
import logging
import requests
from groq import Groq
from dotenv import load_dotenv
from cachetools import TTLCache
from duckduckgo_search import DDGS

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

    def normalize_ticker(self, ticker: str) -> str:
        """
        Remove Yahoo-style suffixes (.NS, .BS, .L, etc.) for cleaner searches.
        Keeps only the root symbol.
        """
        # Removes everything after the first dot, e.g., RELIANCE.NS -> RELIANCE
        return re.split(r"\.", ticker)[0]

    def get_market_context(self, ticker, retries=3):
        logger.info(f"Fetching market context for {ticker}")
        cache_key = f"news_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached market context for {ticker}")
            return self.cache[cache_key]

        # Normalize ticker for news/search
        base_ticker = self.normalize_ticker(ticker)

        news = self.fetch_news(base_ticker, retries)
        if isinstance(news, str):  # error or no news
            return news

        news_summary = "".join(
            [f"- {article['title']} ({article['description']})\n" for article in news[:5]]
        )
        prompt = (
            f"Summarize the market sentiment for {ticker} based on the following news articles:\n"
            f"{news_summary}"
            "Provide a concise summary (100-150 words) focusing on sentiment, key events, and their potential impact on the stock."
        )

        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
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

    def fetch_news(self, base_ticker: str, retries=3):
        """
        Try NewsAPI first, then fallback to DuckDuckGo if no articles or errors occur.
        """
        # --- Primary: NewsAPI ---
        for attempt in range(retries):
            try:
                url = (
                    f"https://newsapi.org/v2/everything?q={base_ticker}+stock"
                    f"&language=en&sortBy=publishedAt&apiKey={self.newsapi_key}"
                )
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                articles = response.json().get("articles", [])
                if articles:
                    news = [
                        {
                            "title": article.get("title") or "No title available",
                            "source": article.get("source", {}).get("name", "Unknown source"),
                            "published_at": article.get("publishedAt") or "Unknown date",
                            "description": article.get("description") or "No description available",
                            "url": article.get("url") or "#"
                        }
                        for article in articles[:5]
                    ]
                    logger.info(f"Fetched {len(news)} news articles for {base_ticker} via NewsAPI")
                    return news
                logger.info(f"No NewsAPI articles found for {base_ticker}")
                break  # Skip retries if no articles, fallback to DuckDuckGo
            except Exception as e:
                logger.error(f"NewsAPI attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        # --- Fallback: DuckDuckGo ---
        try:
            logger.info(f"Falling back to DuckDuckGo for {base_ticker}")
            query = f"{base_ticker} stock news"
            results = DDGS().news(query, region="wt-wt", safesearch="Off", timelimit="w", max_results=10)
            news = []
            for item in results:
                news.append({
                    "title": item.get("title", "No title available"),
                    "source": item.get("source", "DuckDuckGo"),
                    "published_at": item.get("date", "Unknown date"),
                    "description": item.get("body", "No description available"),
                    "url": item.get("url", "#")
                })
            if news:
                logger.info(f"Fetched {len(news)} news articles for {base_ticker} via DuckDuckGo")
                return news
            else:
                return "No recent news found."
        except Exception as e:
            logger.error(f"DuckDuckGo fetch failed: {str(e)}")
            return f"Error fetching news for {base_ticker}."

