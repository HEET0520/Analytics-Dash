import os
import requests
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from cachetools import TTLCache
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

class StockAnalyzerAgent:
    def __init__(self):
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
        logger.info(f"Finnhub API key loaded: {'Yes' if self.finnhub_api_key else 'No'}")
        logger.info(f"Groq API key loaded: {'Yes' if groq_api_key else 'No'}")
        if not all([self.groq_client, self.finnhub_api_key]):
            raise ValueError("Missing API keys in .env file")
        self.cache = TTLCache(maxsize=100, ttl=3600)

    def analyze_stock(self, ticker, market_context, retries=3):
        logger.info(f"Analyzing stock {ticker}")
        cache_key = f"stock_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached analysis for {ticker}")
            return self.cache[cache_key]

        prices = self.fetch_stock_prices(ticker, retries)
        fundamentals = self.fetch_fundamentals(ticker, retries)
        technicals = self.calculate_technicals(prices if not isinstance(prices, str) else [])

        # Proceed with analysis even if some data is missing
        prompt = f"Analyze the stock {ticker} for investment potential based on:\n"
        if not isinstance(prices, str):
            prompt += f"- 30-day closing prices: {prices[:10]}... (latest: {prices[-1]})\n"
            prompt += f"- Technical indicators: SMA20={technicals.get('sma20', 0.0):.2f}, RSI={technicals.get('rsi', 0.0):.2f}\n"
        if not isinstance(fundamentals, str):
            prompt += f"- Fundamentals: Market Cap={fundamentals.get('marketCapitalization', 'N/A')}M, P/E={fundamentals.get('peTTM', 'N/A')}\n"
        prompt += f"- Market context: {market_context[:500]}\n"
        prompt += "Provide a concise analysis (150-200 words) covering trends, risks, opportunities, and an investment recommendation. Use available data; if data is missing, base the analysis on market context alone."

        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=250
                )
                analysis = response.choices[0].message.content
                confidence = self.calculate_confidence(prices if not isinstance(prices, str) else [])
                result = {
                    "analysis": analysis,
                    "confidence": confidence,
                    "prices": prices if not isinstance(prices, str) else [],
                    "fundamentals": fundamentals if not isinstance(fundamentals, str) else {},
                    "technicals": technicals
                }
                self.cache[cache_key] = result
                logger.info(f"Stock analysis completed for {ticker}")
                return result
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        error_msg = "Error generating analysis after retries. Analysis based on market context only."
        result = {
            "analysis": error_msg + f"\nMarket context: {market_context[:200]}",
            "confidence": 0.0,
            "prices": [],
            "fundamentals": {},
            "technicals": technicals
        }
        self.cache[cache_key] = result
        return result

    def fetch_stock_prices(self, ticker, retries=3):
        now = int(time.time())
        for days in [30, 90, 180]:  # Try different time ranges
            from_time = now - days * 86400
            for attempt in range(retries):
                try:
                    url = (
                        f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D"
                        f"&from={from_time}&to={now}&token={self.finnhub_api_key}"
                    )
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    if data.get("s") == "ok" and len(data.get("c", [])) > 0:
                        prices = data["c"][-30:]  # Return last 30 days if available
                        logger.info(f"Fetched {len(prices)} prices for {ticker} over {days} days")
                        return prices
                    logger.warning(f"No data for {ticker} in {days}-day range: {data.get('s', 'Unknown error')}")
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 403:
                        logger.warning(f"Restricted access to price data for {ticker} over {days} days")
                        continue
                    logger.error(f"Price fetch attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Price fetch attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
        logger.error(f"No price data available for {ticker} after trying multiple ranges")
        return f"No price data available for {ticker} in the selected time ranges."

    def fetch_fundamentals(self, ticker, retries=3):
        for attempt in range(retries):
            try:
                # Primary endpoint
                url = (
                    f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all"
                    f"&token={self.finnhub_api_key}"
                )
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get("metric"):
                    logger.info(f"Fetched fundamentals for {ticker}")
                    return data.get("metric", {})
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    logger.warning(f"Restricted access to metric data for {ticker}, trying profile2")
                else:
                    logger.error(f"Fundamentals fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Fundamentals fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        # Fallback to profile2 for basic fundamentals
        try:
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={self.finnhub_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data:
                fallback_fundamentals = {
                    "marketCapitalization": data.get("marketCapitalization"),
                    "peTTM": data.get("pe"),
                    "epsTTM": data.get("eps"),
                }
                logger.info(f"Fetched fallback fundamentals for {ticker} from profile2")
                return fallback_fundamentals
        except Exception as e:
            logger.error(f"Fallback fundamentals fetch failed for {ticker}: {str(e)}")

        logger.error(f"No fundamentals data available for {ticker}")
        return {}

    def calculate_technicals(self, prices):
        if not prices or len(prices) < 20:
            return {"sma20": 0.0, "rsi": 0.0}
        sma20 = np.mean(prices[-20:])
        rsi = self.calculate_rsi(prices)
        return {"sma20": sma20, "rsi": rsi}

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period:
            return 0.0
        deltas = np.diff(prices)
        gains = deltas[deltas > 0]
        losses = -deltas[deltas < 0]
        avg_gain = np.mean(gains[-period:]) if len(gains) >= period else 0
        avg_loss = np.mean(losses[-period:]) if len(losses) >= period else 0
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        return 100 - (100 / (1 + rs))

    def calculate_confidence(self, prices):
        if not prices or isinstance(prices, str):
            return 0.0
        volatility = np.std(prices) / np.mean(prices)
        return max(0.0, 1.0 - volatility)

if __name__ == "__main__":
    agent = StockAnalyzerAgent()
    market_context = "Sample market context for testing."
    result = agent.analyze_stock("MSFT", market_context)
    print(result)