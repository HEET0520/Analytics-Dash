from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from head_agent import HeadAgent
import logging
from pydantic import BaseModel

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
    keyFactors: list[str]
    targetPrice: dict[str, float]
    recommendation: str

@app.get("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_stock(ticker: str):
    logger.info(f"Received request to analyze {ticker}")
    try:
        head_agent = HeadAgent()
    except Exception as e:
        logger.error(f"Failed to initialize HeadAgent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server initialization error: {str(e)}")

    result = head_agent.analyze_stock(ticker.upper())
    if "error" in result:
        logger.error(f"Analysis failed: {result['error']}")
        error_detail = result["error"]
        if "Finnhub API error" in error_detail or "not supported" in error_detail:
            error_detail += " Try major tickers like TSLA, MSFT, or AAPL."
        raise HTTPException(status_code=400, detail=error_detail)

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

        # Use default price if prices are unavailable
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
            "recommendation": recommendation
        }
        logger.info(f"Analysis successful for {ticker}")
        return response
    except Exception as e:
        logger.error(f"Error processing response for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing analysis: {str(e)}. Try major tickers like TSLA, MSFT, or AAPL.")

@app.get("/validate-ticker/{ticker}")
async def validate_ticker(ticker: str):
    try:
        head_agent = HeadAgent()
        stock_analyzer = head_agent.stock_analyzer_agent
        is_valid = stock_analyzer.validate_ticker(ticker.upper())
        return {"ticker": ticker, "valid": is_valid}
    except Exception as e:
        logger.error(f"Ticker validation failed for {ticker}: {str(e)}")
        return {"ticker": ticker, "valid": False, "error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)