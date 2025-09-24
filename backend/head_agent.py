import os
from market_context import MarketContextAgent
from stock_analyzer import StockAnalyzerAgent
from fin_analyzer import FinAnalyzerAgent
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class HeadAgent:
    def __init__(self):
        logger.info("Initializing HeadAgent")
        try:
            self.market_context_agent = MarketContextAgent()
            self.stock_analyzer_agent = StockAnalyzerAgent()
            self.fin_analyzer_agent = FinAnalyzerAgent()
            logger.info("All agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise

    def is_valid_ticker(self, ticker):
        """Validate ticker, allowing for Indian stock suffixes like .NS or .BO."""
        # Remove exchange suffix (e.g., .NS, .BO) and check base ticker
        base_ticker = ticker.split('.')[0] if '.' in ticker else ticker
        return base_ticker.isalnum() and 1 <= len(base_ticker) <= 10 and (ticker.endswith(('.NS', '.BO')) or len(ticker) == len(base_ticker))

    def analyze_stock(self, ticker):
        if not self.is_valid_ticker(ticker):
            logger.error(f"Invalid ticker: {ticker}")
            raise ValueError("Invalid ticker symbol. Use 1-10 alphanumeric characters, optionally with .NS or .BO suffix for Indian stocks.")

        logger.info(f"Starting analysis for {ticker}")
        try:
            market_context = self.market_context_agent.get_market_context(ticker)
            stock_result = self.stock_analyzer_agent.analyze_stock(ticker, market_context)
            if "error" in stock_result:
                logger.error(f"Stock analysis failed for {ticker}: {stock_result['error']}")
                return {"error": stock_result["error"]}

            fundamentals_analysis = self.fin_analyzer_agent.analyze_fundamentals(ticker, stock_result.get("income_statement", {}))
            result = {
                "ticker": ticker,
                "timestamp": datetime.utcnow().isoformat(),
                "market_context": market_context,
                "stock_analysis": stock_result["analysis"],
                "confidence": stock_result["confidence"],
                "prices": stock_result["prices"],
                "technicals": stock_result["technicals"],
                "fundamentals": stock_result["income_statement"],
                "fundamentals_analysis": fundamentals_analysis
            }
            self.save_analysis(result)
            logger.info(f"Analysis completed for {ticker}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}

    def save_analysis(self, result):
        if "error" in result:
            return
        filename = f"analysis_{result['ticker']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved analysis to {filename}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {str(e)}")

if __name__ == "__main__":
    import sys
    head_agent = HeadAgent()
    ticker = input("Enter stock ticker (e.g., TSLA, RELIANCE.NS): ").strip().upper()
    result = head_agent.analyze_stock(ticker)
    print(json.dumps(result, indent=2))