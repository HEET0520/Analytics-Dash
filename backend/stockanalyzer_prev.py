import os
import requests
import yfinance as yf
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from cachetools import TTLCache
import time
import logging
from datetime import datetime, timedelta

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

    def fetch_stock_prices(self, ticker, retries=3):
        """Fetch 1 year of historical OHLCV data from yfinance."""
        logger.info(f"Fetching historical prices for {ticker} from yfinance")
        cache_key = f"prices_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached prices for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)  # Updated to 1 year
                hist = stock.history(start=start_date, end=end_date, interval="1d")
                if hist.empty:
                    logger.warning(f"No price data found for {ticker} on yfinance")
                    return f"No price data available for {ticker}."

                prices = [
                    {
                        "date": index.strftime('%Y-%m-%d'),
                        "open": round(row['Open'], 2),
                        "high": round(row['High'], 2),
                        "low": round(row['Low'], 2),
                        "close": round(row['Close'], 2),
                        "volume": int(row['Volume'])
                    }
                    for index, row in hist.iterrows()
                ]
                self.cache[cache_key] = prices
                logger.info(f"Fetched {len(prices)} price points for {ticker} from yfinance")
                return prices
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed fetching prices from yfinance for {ticker}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No price data available for {ticker} after {retries} retries")
        return f"No price data available for {ticker} after {retries} retries."


    def fetch_fundamentals(self, ticker, retries=3):
        """Fetch fundamentals from Finnhub's /stock/metric and /stock/profile2."""
        logger.info(f"Fetching fundamentals for {ticker} from Finnhub")
        cache_key = f"fundamentals_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached fundamentals for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                url = (
                    f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all"
                    f"&token={self.finnhub_api_key}"
                )
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get("metric"):
                    self.cache[cache_key] = data["metric"]
                    logger.info(f"Fetched fundamentals for {ticker}")
                    return data["metric"]
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    logger.error(f"Fundamentals fetch failed: Invalid or restricted Finnhub API key for {ticker}")
                    return f"Invalid or restricted Finnhub API key for {ticker}."
                logger.error(f"Fundamentals fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Fundamentals fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        try:
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={self.finnhub_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data:
                fallback_fundamentals = {
                    "marketCapitalization": data.get("marketCapitalization"),
                    "peTTM": data.get("pe"),
                    "epsTTM": data.get("eps")
                }
                self.cache[cache_key] = fallback_fundamentals
                logger.info(f"Fetched fallback fundamentals for {ticker} from profile2")
                return fallback_fundamentals
        except Exception as e:
            logger.error(f"Fallback fundamentals fetch failed for {ticker}: {str(e)}")

        logger.error(f"No fundamentals data available for {ticker}")
        return {}

    def fetch_basic_financials(self, ticker, retries=3):
        """Fetch basic financials from Finnhub's /stock/metrics."""
        logger.info(f"Fetching basic financials for {ticker} from Finnhub")
        cache_key = f"basic_financials_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached basic financials for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&token={self.finnhub_api_key}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if data:
                    basic_financials = {
                        "name": data.get("name", "N/A"),
                        "ticker": data.get("ticker", ticker),
                        "exchange": data.get("exchange", "N/A"),
                        "industry": data.get("finnhubIndustry", "N/A"),
                        "marketCapitalization": data.get("marketCapitalization", None),
                        "shareOutstanding": data.get("shareOutstanding", None),
                        "ipo": data.get("ipo", "N/A"),
                        "weburl": data.get("weburl", "N/A")
                    }
                    self.cache[cache_key] = basic_financials
                    logger.info(f"Fetched basic financials for {ticker}")
                    return basic_financials
                return f"No basic financials available for {ticker}."
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    logger.error(f"Basic financials fetch failed: Invalid or restricted Finnhub API key for {ticker}")
                    return f"Invalid or restricted Finnhub API key for {ticker}."
                logger.error(f"Basic financials fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Basic financials fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No basic financials available for {ticker}")
        return f"No basic financials available for {ticker}."

    def fetch_financials_reported(self, ticker, retries=3):
        """Fetch financials as reported from Finnhub's /financials-reported."""
        logger.info(f"Fetching financials as reported for {ticker} from Finnhub")
        cache_key = f"financials_reported_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached financials as reported for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                url = f"https://finnhub.io/api/v1/stock/financials-reported?symbol={ticker}&token={self.finnhub_api_key}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get("data"):
                    financials = [
                        {
                            "period": report.get("period", "N/A"),
                            "year": report.get("year", None),
                            "quarter": report.get("quarter", None),
                            "revenue": report.get("financials", {}).get("income_statement", {}).get("revenue", None),
                            "netIncome": report.get("financials", {}).get("income_statement", {}).get("net_income", None),
                            "eps": report.get("financials", {}).get("income_statement", {}).get("eps", None)
                        }
                        for report in data["data"][:4]  # Last 4 quarters
                    ]
                    self.cache[cache_key] = financials
                    logger.info(f"Fetched {len(financials)} financial reports for {ticker}")
                    return financials
                return f"No financials as reported available for {ticker}."
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    logger.error(f"Financials reported fetch failed: Invalid or restricted Finnhub API key for {ticker}")
                    return f"Invalid or restricted Finnhub API key for {ticker}."
                logger.error(f"Financials reported fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Financials reported fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No financials as reported available for {ticker}")
        return f"No financials as reported available for {ticker}."

    def fetch_company_news(self, ticker, retries=3):
        """Fetch company news from Finnhub's /company-news."""
        logger.info(f"Fetching company news for {ticker} from Finnhub")
        cache_key = f"news_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached news for {ticker}")
            return self.cache[cache_key]

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        for attempt in range(retries):
            try:
                url = (
                    f"https://finnhub.io/api/v1/company-news?symbol={ticker}"
                    f"&from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}"
                    f"&token={self.finnhub_api_key}"
                )
                response = requests.get(url)
                response.raise_for_status()
                articles = response.json()
                if not articles:
                    logger.info(f"No news articles found for {ticker}")
                    return f"No recent news found for {ticker}."
                news = [
                    {
                        "headline": article.get("headline", "No headline"),
                        "source": article.get("source", "Unknown source"),
                        "datetime": datetime.fromtimestamp(article.get("datetime", 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        "summary": article.get("summary", "No summary"),
                        "url": article.get("url", "#")
                    }
                    for article in articles[:5]
                ]
                self.cache[cache_key] = news
                logger.info(f"Fetched {len(news)} news articles for {ticker}")
                return news
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    logger.error(f"News fetch failed: Invalid or restricted Finnhub API key for {ticker}")
                    return f"Invalid or restricted Finnhub API key for {ticker}."
                logger.error(f"News fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"News fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"Error fetching news for {ticker} after {retries} attempts")
        return f"Error fetching news for {ticker} after {retries} attempts."

    def calculate_technicals(self, prices):
        """Calculate technical indicators (SMA20, RSI) from price data."""
        if not prices or isinstance(prices, str) or len(prices) < 20:
            logger.warning("Insufficient price data for technical analysis")
            return {"sma20": 0.0, "rsi": 0.0}
        closes = [p["close"] for p in prices]
        sma20 = np.mean(closes[-20:])
        rsi = self.calculate_rsi(closes)
        return {"sma20": round(sma20, 2), "rsi": round(rsi, 2)}

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI for given prices."""
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
        """Calculate confidence score based on price volatility."""
        if not prices or isinstance(prices, str):
            return 0.0
        closes = [p["close"] for p in prices]
        volatility = np.std(closes) / np.mean(closes)
        return max(0.0, round(1.0 - volatility, 2))

    def analyze_stock(self, ticker, market_context, retries=3):
        """Analyze stock using combined data."""
        logger.info(f"Analyzing stock {ticker}")
        cache_key = f"stock_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached analysis for {ticker}")
            return self.cache[cache_key]

        prices = self.fetch_stock_prices(ticker, retries)
        fundamentals = self.fetch_fundamentals(ticker, retries)
        technicals = self.calculate_technicals(prices)

        prompt = f"Analyze the stock {ticker} for investment potential based on:\n"
        if not isinstance(prices, str):
            prompt += f"- 30-day closing prices: {[p['close'] for p in prices[-10:]]} (latest: {prices[-1]['close']})\n"
            prompt += f"- Technical indicators: SMA20={technicals.get('sma20', 0.0):.2f}, RSI={technicals.get('rsi', 0.0):.2f}\n"
        if not isinstance(fundamentals, str):
            prompt += f"- Fundamentals: Market Cap={fundamentals.get('marketCapitalization', 'N/A')}M, P/E={fundamentals.get('peTTM', 'N/A')}\n"
        prompt += f"- Market context: {market_context[:500]}\n"
        prompt += "Provide a concise analysis (150-200 words) covering trends, risks, opportunities, and an investment recommendation."

        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=250
                )
                analysis = response.choices[0].message.content
                confidence = self.calculate_confidence(prices)
                result = {
                    "analysis": analysis,
                    "confidence": confidence,
                    "prices": [p["close"] for p in prices] if not isinstance(prices, str) else [],
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

        error_msg = "Error generating analysis. Based on market context only."
        result = {
            "analysis": error_msg + f"\nMarket context: {market_context[:200]}",
            "confidence": 0.0,
            "prices": [],
            "fundamentals": {},
            "technicals": technicals
        }
        self.cache[cache_key] = result
        return result

    def fetch_all_data(self, ticker, retries=3):
        """Fetch all data (prices, fundamentals, technicals, basic financials, financials reported, news) and return as JSON."""
        logger.info(f"Fetching all data for {ticker}")
        cache_key = f"all_data_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached all data for {ticker}")
            return self.cache[cache_key]

        prices = self.fetch_stock_prices(ticker, retries)
        fundamentals = self.fetch_fundamentals(ticker, retries)
        technicals = self.calculate_technicals(prices)
        basic_financials = self.fetch_basic_financials(ticker, retries)
        financials_reported = self.fetch_financials_reported(ticker, retries)
        company_news = self.fetch_company_news(ticker, retries)

        result = {
            "ticker": ticker,
            "historical_prices": prices if not isinstance(prices, str) else [],
            "fundamentals": fundamentals if not isinstance(fundamentals, str) else {},
            "technicals": technicals,
            "basic_financials": basic_financials if not isinstance(basic_financials, str) else {},
            "financials_reported": financials_reported if not isinstance(financials_reported, str) else [],
            "company_news": company_news if not isinstance(company_news, str) else [],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "errors": []
        }

        # Collect errors
        if isinstance(prices, str):
            result["errors"].append(prices)
        if isinstance(fundamentals, str):
            result["errors"].append(fundamentals)
        if isinstance(basic_financials, str):
            result["errors"].append(basic_financials)
        if isinstance(financials_reported, str):
            result["errors"].append(financials_reported)
        if isinstance(company_news, str):
            result["errors"].append(company_news)

        self.cache[cache_key] = result
        logger.info(f"Fetched all data for {ticker}")
        return result