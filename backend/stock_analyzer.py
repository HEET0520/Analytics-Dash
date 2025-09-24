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
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
        logger.info(f"Groq API key loaded: {'Yes' if groq_api_key else 'No'}")
        if not self.groq_client:
            raise ValueError("Missing GROQ_API_KEY in .env file")
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
                start_date = end_date - timedelta(days=365)
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

    def fetch_income_statement(self, ticker, retries=3):
        """Fetch quarterly income statement data from yfinance."""
        logger.info(f"Fetching income statement for {ticker} from yfinance")
        cache_key = f"income_stmt_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached income statement for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                income_stmt = stock.get_income_stmt(freq="quarterly")
                if income_stmt.empty:
                    logger.warning(f"No income statement data found for {ticker}")
                    return f"No income statement data available for {ticker}."
                data = income_stmt.to_dict()
                formatted_data = {
                    "total_revenue": data.get("TotalRevenue", {}),
                    "net_income": data.get("NetIncome", {}),
                    "gross_profit": data.get("GrossProfit", {}),
                    "operating_income": data.get("OperatingIncome", {})
                }
                self.cache[cache_key] = formatted_data
                logger.info(f"Fetched income statement for {ticker}")
                return formatted_data
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed fetching income statement for {ticker}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No income statement data available for {ticker}")
        return f"No income statement data available for {ticker}."

    def fetch_cash_flow(self, ticker, retries=3):
        """Fetch quarterly cash flow data from yfinance."""
        logger.info(f"Fetching cash flow for {ticker} from yfinance")
        cache_key = f"cash_flow_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached cash flow for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                cash_flow = stock.get_cash_flow(freq="quarterly")
                if cash_flow.empty:
                    logger.warning(f"No cash flow data found for {ticker}")
                    return f"No cash flow data available for {ticker}."
                data = cash_flow.to_dict()
                formatted_data = {
                    "operating_cash_flow": data.get("OperatingCashFlow", {}),
                    "free_cash_flow": data.get("FreeCashFlow", {})
                }
                self.cache[cache_key] = formatted_data
                logger.info(f"Fetched cash flow for {ticker}")
                return formatted_data
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed fetching cash flow for {ticker}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No cash flow data available for {ticker}")
        return f"No cash flow data available for {ticker}."

    def fetch_eps_data(self, ticker, retries=3):
        """Fetch EPS trend and revision data from yfinance."""
        logger.info(f"Fetching EPS trend and revision for {ticker} from yfinance")
        cache_key = f"eps_data_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached EPS data for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                eps_trend = getattr(stock, 'get_eps_trend', lambda: None)()
                eps_revision = getattr(stock, 'get_eps_revision', lambda: None)()
                if eps_trend is None and eps_revision is None:
                    logger.warning(f"No EPS data found for {ticker}")
                    return f"No EPS data available for {ticker}."
                formatted_data = {
                    "eps_trend": (eps_trend.to_dict() if hasattr(eps_trend, 'empty') and not eps_trend.empty else {}) if eps_trend is not None else {},
                    "eps_revision": (eps_revision.to_dict() if hasattr(eps_revision, 'empty') and not eps_revision.empty else {}) if eps_revision is not None else {}
                }
                self.cache[cache_key] = formatted_data
                logger.info(f"Fetched EPS data for {ticker}")
                return formatted_data
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed fetching EPS data for {ticker}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No EPS data available for {ticker}")
        return f"No EPS data available for {ticker}."

    def fetch_analyst_recommendations(self, ticker, retries=3):
        """Fetch analyst price targets and recommendations from yfinance."""
        logger.info(f"Fetching analyst recommendations for {ticker} from yfinance")
        cache_key = f"analyst_recommendations_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached analyst recommendations for {ticker}")
            return self.cache[cache_key]

        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                price_targets = stock.get_analyst_price_targets()
                if not price_targets:
                    logger.warning(f"No analyst recommendations found for {ticker}")
                    return f"No analyst recommendations available for {ticker}."
                formatted_data = {
                    "mean_price_target": price_targets.get("mean", None),
                    "high_price_target": price_targets.get("high", None),
                    "low_price_target": price_targets.get("low", None),
                    "number_of_analysts": price_targets.get("numberOfAnalystOpinions", None)
                }
                self.cache[cache_key] = formatted_data
                logger.info(f"Fetched analyst recommendations for {ticker}")
                return formatted_data
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed fetching analyst recommendations for {ticker}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        logger.error(f"No analyst recommendations available for {ticker}")
        return f"No analyst recommendations available for {ticker}."

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

    def calculate_confidence(self, prices, analyst_recommendations):
        """Calculate confidence score based on price volatility and analyst coverage."""
        if not prices or isinstance(prices, str):
            return 0.0
        closes = [p["close"] for p in prices]
        volatility = np.std(closes) / np.mean(closes) if closes else 0.0
        volatility_score = max(0.0, 1.0 - volatility)
        if isinstance(analyst_recommendations, str):
            num_analysts = 0
        else:
            # Handle None safely
            num_analysts = analyst_recommendations.get("number_of_analysts") or 0
            try:
                num_analysts = int(num_analysts)
            except Exception:
                num_analysts = 0
        analyst_score = 0.5 if num_analysts > 0 else 0.0
        return round(0.7 * volatility_score + 0.3 * analyst_score, 2)

    def analyze_stock(self, ticker, market_context, retries=3):
        """Analyze stock using combined yfinance data."""
        logger.info(f"Analyzing stock {ticker}")
        cache_key = f"stock_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached analysis for {ticker}")
            return self.cache[cache_key]

        prices = self.fetch_stock_prices(ticker, retries)
        income_stmt = self.fetch_income_statement(ticker, retries)
        cash_flow = self.fetch_cash_flow(ticker, retries)
        eps_data = self.fetch_eps_data(ticker, retries)
        analyst_recommendations = self.fetch_analyst_recommendations(ticker, retries)
        technicals = self.calculate_technicals(prices)

        prompt = f"Analyze the stock {ticker} for investment potential based on:\n"
        if not isinstance(prices, str):
            prompt += f"- 30-day closing prices: {[p['close'] for p in prices[-10:]]} (latest: {prices[-1]['close']})\n"
            prompt += f"- Technical indicators: SMA20={technicals.get('sma20', 0.0):.2f}, RSI={technicals.get('rsi', 0.0):.2f}\n"
        if not isinstance(income_stmt, str):
            latest_quarter = max(income_stmt["total_revenue"].keys(), default=None) if income_stmt["total_revenue"] else None
            if latest_quarter:
                prompt += (
                    f"- Income Statement (latest quarter {latest_quarter}):\n"
                    f"  - Total Revenue: {income_stmt['total_revenue'].get(latest_quarter, 'N/A')}\n"
                    f"  - Net Income: {income_stmt['net_income'].get(latest_quarter, 'N/A')}\n"
                    f"  - Operating Income: {income_stmt['operating_income'].get(latest_quarter, 'N/A')}\n"
                )
        if not isinstance(cash_flow, str):
            latest_quarter = max(cash_flow["operating_cash_flow"].keys(), default=None) if cash_flow["operating_cash_flow"] else None
            if latest_quarter:
                prompt += (
                    f"- Cash Flow (latest quarter {latest_quarter}):\n"
                    f"  - Operating Cash Flow: {cash_flow['operating_cash_flow'].get(latest_quarter, 'N/A')}\n"
                    f"  - Free Cash empujar: {cash_flow['free_cash_flow'].get(latest_quarter, 'N/A')}\n"
                )
        if not isinstance(eps_data, str):
            prompt += (
                f"- EPS Data:\n"
                f"  - Current Quarter EPS Estimate: {eps_data['eps_trend'].get('currentQuarter', {}).get('epsEstimate', 'N/A')}\n"
                f"  - EPS Revision (Up/Down): {eps_data['eps_revision'].get('currentQuarter', {}).get('numberOfAnalystsRevisedUp', 0)} up, "
                f"{eps_data['eps_revision'].get('currentQuarter', {}).get('numberOfAnalystsRevisedDown', 0)} down\n"
            )
        if not isinstance(analyst_recommendations, str):
            prompt += (
                f"- Analyst Recommendations:\n"
                f"  - Mean Price Target: {analyst_recommendations.get('mean_price_target', 'N/A')}\n"
                f"  - Number of Analysts: {analyst_recommendations.get('number_of_analysts', 'N/A')}\n"
            )
        prompt += f"- Market context: {market_context[:500]}\n"
        prompt += "Provide a concise analysis (150-200 words) covering trends, risks, opportunities, and an investment recommendation."

        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=250
                )
                analysis = response.choices[0].message.content
                confidence = self.calculate_confidence(prices, analyst_recommendations)
                result = {
                    "analysis": analysis,
                    "confidence": confidence,
                    "prices": prices if not isinstance(prices, str) else [],
                    "income_statement": income_stmt if not isinstance(income_stmt, str) else {},
                    "cash_flow": cash_flow if not isinstance(cash_flow, str) else {},
                    "eps_data": eps_data if not isinstance(eps_data, str) else {},
                    "analyst_recommendations": analyst_recommendations if not isinstance(analyst_recommendations, str) else {},
                    "technicals": technicals
                }
                self.cache[cache_key] = result
                logger.info(f"Stock analysis completed for {ticker}")
                return result
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        # Fallback: preserve fetched data even if LLM call failed
        error_msg = "Error generating analysis. Based on available data."
        confidence = self.calculate_confidence(prices if not isinstance(prices, str) else [], analyst_recommendations if not isinstance(analyst_recommendations, str) else {})
        result = {
            "analysis": error_msg + f"\nMarket context: {market_context[:200]}",
            "confidence": confidence,
            "prices": prices if not isinstance(prices, str) else [],
            "income_statement": income_stmt if not isinstance(income_stmt, str) else {},
            "cash_flow": cash_flow if not isinstance(cash_flow, str) else {},
            "eps_data": eps_data if not isinstance(eps_data, str) else {},
            "analyst_recommendations": analyst_recommendations if not isinstance(analyst_recommendations, str) else {},
            "technicals": technicals
        }
        self.cache[cache_key] = result
        return result

    def fetch_all_data(self, ticker, retries=3):
        """Fetch all data (prices, income statement, cash flow, EPS data, analyst recommendations, technicals) and return as JSON."""
        logger.info(f"Fetching all data for {ticker}")
        cache_key = f"all_data_{ticker}"
        if cache_key in self.cache:
            logger.info(f"Returning cached all data for {ticker}")
            return self.cache[cache_key]

        prices = self.fetch_stock_prices(ticker, retries)
        income_stmt = self.fetch_income_statement(ticker, retries)
        cash_flow = self.fetch_cash_flow(ticker, retries)
        eps_data = self.fetch_eps_data(ticker, retries)
        analyst_recommendations = self.fetch_analyst_recommendations(ticker, retries)
        technicals = self.calculate_technicals(prices)

        result = {
            "ticker": ticker,
            "historical_prices": prices if not isinstance(prices, str) else [],
            "income_statement": income_stmt if not isinstance(income_stmt, str) else {},
            "cash_flow": cash_flow if not isinstance(cash_flow, str) else {},
            "eps_data": eps_data if not isinstance(eps_data, str) else {},
            "analyst_recommendations": analyst_recommendations if not isinstance(analyst_recommendations, str) else {},
            "technicals": technicals,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "errors": []
        }

        # Collect errors
        if isinstance(prices, str):
            result["errors"].append(prices)
        if isinstance(income_stmt, str):
            result["errors"].append(income_stmt)
        if isinstance(cash_flow, str):
            result["errors"].append(cash_flow)
        if isinstance(eps_data, str):
            result["errors"].append(eps_data)
        if isinstance(analyst_recommendations, str):
            result["errors"].append(analyst_recommendations)

        self.cache[cache_key] = result
        logger.info(f"Fetched all data for {ticker}")
        return result