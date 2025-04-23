from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from head_agent import HeadAgent
import logging
from pydantic import BaseModel
import os
import shutil
from tasks import analyze_document

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
    dataAvailability: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    summary: str = ""
    analysis_results: str = ""
    financial_metrics: str = ""
    key_insights: list[str] = []
    sentiment: str = "neutral"
    recommendations: list[str] = []
    error: str = ""

@app.post("/analyze/", response_model=TaskStatus)
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Received file upload: {file.filename}")
    try:
        # Save the file temporarily
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Start the Celery task
        task = analyze_document.delay(file_path, file.filename)
        return {"task_id": task.id, "status": "pending"}
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    task = AsyncResult(task_id)
    if task.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif task.state == "SUCCESS":
        result = task.result
        if result.get("status") == "failed":
            return {
                "task_id": task_id,
                "status": "failed",
                "error": result.get("error", "Unknown error")
            }
        return {
            "task_id": task_id,
            "status": "completed",
            "summary": result.get("summary", ""),
            "analysis_results": result.get("analysis_results", ""),
            "financial_metrics": result.get("financial_metrics", ""),
            "key_insights": result.get("key_insights", []),
            "sentiment": result.get("sentiment", "neutral"),
            "recommendations": result.get("recommendations", [])
        }
    elif task.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(task.result)
        }
    else:
        return {"task_id": task_id, "status": task.state}

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