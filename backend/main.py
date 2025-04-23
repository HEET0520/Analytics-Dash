from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from head_agent import HeadAgent
import logging
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    summary: str
    sentiment: str
    confidence: float
    keyFactors: List[str]
    targetPrice: Dict[str, float]
    recommendation: str
    dataAvailability: str

class PriceData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class PricesResponse(BaseModel):
    ticker: str
    prices: List[PriceData]
    error: str = ""

class NewsItem(BaseModel):
    title: str
    source: str
    published_at: str
    description: str
    url: str

class MarketContextResponse(BaseModel):
    ticker: str
    news: List[NewsItem]
    error: str = ""

class AllDataResponse(BaseModel):
    ticker: str
    historical_prices: List[PriceData]
    fundamentals: Dict[str, Any]
    technicals: Dict[str, float]
    basic_financials: Dict[str, Any]
    financials_reported: List[Dict[str, Any]]
    company_news: List[Dict[str, Any]]
    timestamp: str
    errors: List[str]

@app.get("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_stock(ticker: str):
    logger.info(f"Received request to analyze {ticker}")
    try:
        head_agent = HeadAgent()
    except Exception as e:
        logger.error(f"Failed to initialize HeadAgent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server initialization error: {str(e)}")

    result = head_agent.analyze_stock(ticker.upper())
    if "error" in result and "after retries" in result["analysis"]:
        logger.warning(f"Partial analysis for {ticker} due to data issues")
        result["analysis"] = result["analysis"].replace("Error generating analysis", "Partial analysis generated")

    try:
        key_factors = []
        for line in (result["stock_analysis"].split("\n") + result["fundamentals_analysis"].split("\n")):
            if line.strip().startswith("-") or line.strip().startswith("*"):
                key_factors.append(line.strip()[1:].strip())
        key_factors = key_factors[:5] or ["No key factors identified due to limited data."]

        sentiment_words = result["stock_analysis"].lower() + result["market_context"].lower()
        positive_words = ["strong", "growth", "bullish", "positive", "expansion"]
        negative_words = ["weak", "decline", "bearish", "negative", "risk"]
        positive_count = sum(sentiment_words.count(word) for word in positive_words)
        negative_count = sum(sentiment_words.count(word) for word in negative_words)
        sentiment = (
            "bullish" if positive_count > negative_count
            else "bearish" if negative_count > positive_count
            else "neutral"
        )

        latest_price = result["prices"][-1] if result["prices"] else 100.0
        pe_ratio = result["fundamentals"].get("peTTM", 20.0) if not isinstance(result["fundamentals"], str) else 20.0
        target_mid = latest_price * (1 + (pe_ratio / 100))
        target_low = target_mid * 0.9
        target_high = target_mid * 1.1

        recommendation = (
            "buy" if sentiment == "bullish" and result["confidence"] > 0.7
            else "sell" if sentiment == "bearish" and result["confidence"] > 0.7
            else "hold"
        )

        data_availability = (
            "Full data available" if result["prices"] and result["fundamentals"]
            else "Partial data (prices missing)" if not result["prices"] and result["fundamentals"]
            else "Partial data (fundamentals missing)" if result["prices"] and not result["fundamentals"]
            else "Limited data (market context only)"
        )

        response = {
            "summary": (
                f"{result['stock_analysis']}\n\n"
                f"Fundamentals: {result['fundamentals_analysis']}\n\n"
                f"Market Context: {result['market_context']}"
            ),
            "sentiment": sentiment,
            "confidence": result["confidence"] * 100,
            "keyFactors": key_factors,
            "targetPrice": {
                "low": round(target_low, 2),
                "mid": round(target_mid, 2),
                "high": round(target_high, 2)
            },
            "recommendation": recommendation,
            "dataAvailability": data_availability
        }
        logger.info(f"Analysis successful for {ticker}")
        return response
    except Exception as e:
        logger.error(f"Error processing response for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing analysis: {str(e)}")

@app.get("/prices/{ticker}", response_model=PricesResponse)
async def get_stock_prices(ticker: str):
    logger.info(f"Received request for prices of {ticker}")
    try:
        head_agent = HeadAgent()
        prices = head_agent.stock_analyzer_agent.fetch_stock_prices(ticker.upper(), retries=3)
        
        if isinstance(prices, str):
            logger.warning(f"No price data found for {ticker}: {prices}")
            return PricesResponse(ticker=ticker, prices=[], error=prices)

        logger.info(f"Successfully retrieved {len(prices)} price points for {ticker}")
        return PricesResponse(ticker=ticker, prices=prices, error="")
    except Exception as e:
        logger.error(f"Error retrieving prices for {ticker}: {str(e)}")
        return PricesResponse(
            ticker=ticker,
            prices=[],
            error=f"Failed to retrieve prices: {str(e)}"
        )

@app.get("/market-context/{ticker}", response_model=MarketContextResponse)
async def get_market_context(ticker: str):
    logger.info(f"Received request for market context of {ticker}")
    try:
        head_agent = HeadAgent()
        news = head_agent.market_context_agent.fetch_news(ticker.upper(), retries=3)
        
        if isinstance(news, str):
            logger.warning(f"No news data found for {ticker}: {news}")
            return MarketContextResponse(ticker=ticker, news=[], error=news)

        logger.info(f"Successfully retrieved {len(news)} news articles for {ticker}")
        return MarketContextResponse(ticker=ticker, news=news, error="")
    except Exception as e:
        logger.error(f"Error retrieving market context for {ticker}: {str(e)}")
        return MarketContextResponse(
            ticker=ticker,
            news=[],
            error=f"Failed to retrieve market context: {str(e)}"
        )

@app.get("/all-data/{ticker}", response_model=AllDataResponse)
async def get_all_data(ticker: str):
    logger.info(f"Received request for all data of {ticker}")
    try:
        head_agent = HeadAgent()
        data = head_agent.stock_analyzer_agent.fetch_all_data(ticker.upper(), retries=3)
        logger.info(f"Successfully retrieved all data for {ticker}")
        return AllDataResponse(**data)
    except Exception as e:
        logger.error(f"Error retrieving all data for {ticker}: {str(e)}")
        return AllDataResponse(
            ticker=ticker,
            historical_prices=[],
            fundamentals={},
            technicals={"sma20": 0.0, "rsi": 0.0},
            basic_financials={},
            financials_reported=[],
            company_news=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            errors=[f"Failed to retrieve all data: {str(e)}"]
        )

@app.get("/validate-ticker/{ticker}")
async def validate_ticker(ticker: str):
    try:
        head_agent = HeadAgent()
        stock_analyzer = head_agent.stock_analyzer_agent
        return {"ticker": ticker, "valid": True}
    except Exception as e:
        logger.error(f"Ticker validation failed for {ticker}: {str(e)}")
        return {"ticker": ticker, "valid": False, "error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)