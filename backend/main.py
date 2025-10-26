from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from head_agent import HeadAgent
import time
from realtime_prices import RealTimePriceService
from realtime_ws import manager, stream_prices
from document_analyzer import analyze_report, process_document_task, get_task_status, extract_text_from_pdf, process_graphs, extract_images_from_pdf, extract_text_from_image
import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from io import BytesIO
from PIL import Image
import numpy as np
import asyncio
from head_agent import HeadAgent
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock and Document Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for stock analysis
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

# Updated Pydantic model for document analysis
class DocumentAnalysisResponse(BaseModel):
    analysis_results: str
    financial_metrics_table: str
    recommendation: str
    processing_time: str

class AnalysisStatus(BaseModel):
    task_id: str
    status: str
    analysis_results: Optional[str] = None
    financial_metrics_table: Optional[str] = None
    recommendation: Optional[str] = None
    processing_time: Optional[str] = None
    error: Optional[str] = None

# Stock analysis endpoints
@app.get("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_stock(ticker: str):
    logger.info(f"Received request to analyze {ticker}")
    try:
        head_agent = HeadAgent()
    except Exception as e:
        logger.error(f"Failed to initialize HeadAgent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server initialization error: {str(e)}")

    try:
        result = head_agent.analyze_stock(ticker.upper())
        if "error" in result:
            logger.warning(f"Analysis failed for {ticker}: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

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

        latest_price = result["prices"][-1]["close"] if result["prices"] else 100.0
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
    except ValueError as e:
        logger.error(f"Invalid ticker for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
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

# Document analysis endpoints
@app.post("/analyze/", response_model=AnalysisStatus)
async def analyze_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Submit a financial document (PDF or image) for asynchronous analysis.
    Returns a task ID to check the status of analysis.
    
    - **file**: Upload a PDF or image file (max 10MB)
    """
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in ["pdf", "png", "jpg", "jpeg", "bmp", "gif", "tiff"]:
        logger.error(f"Unsupported file format: {file_extension}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats: pdf, png, jpg, jpeg, bmp, gif, tiff")
    
    # Validate file size (max 10MB)
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        logger.error(f"File {file.filename} exceeds 10MB limit")
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    task_id = f"task_{int(time.time())}_{file.filename}"
    
    background_tasks.add_task(
        process_document_task,
        task_id,
        file_bytes,
        file_extension
    )
    
    logger.info(f"Started asynchronous document analysis task {task_id}")
    return AnalysisStatus(task_id=task_id, status="processing")

@app.post("/analyze_sync/", response_model=DocumentAnalysisResponse)
async def analyze_document_sync(file: UploadFile = File(...)):
    """
    Analyze a financial document (PDF or image) synchronously.
    Returns analysis results, financial metrics table, recommendation, and processing time.
    
    - **file**: Upload a PDF or image file (max 10MB)
    """
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in ["pdf", "png", "jpg", "jpeg", "bmp", "gif", "tiff"]:
        logger.error(f"Unsupported file format: {file_extension}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Supported formats: pdf, png, jpg, jpeg, bmp, gif, tiff")
    
    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        logger.error(f"File {file.filename} exceeds 10MB limit")
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        if file_extension == "pdf":
            text = extract_text_from_pdf(contents)
            images = extract_images_from_pdf(contents)
            graph_text = await process_graphs(images)
        else:
            image = Image.open(BytesIO(contents))
            image_np = np.array(image)
            text = extract_text_from_image(image_np)
            graph_text = None
        
        # Properly await the async analyze_report function
        analysis_results, metrics_table, recommendation, processing_time = await analyze_report(text, graph_text)
        
        logger.info(f"Synchronous document analysis completed for {file.filename} in {processing_time:.2f} seconds")
        return DocumentAnalysisResponse(
            analysis_results=analysis_results,
            financial_metrics_table=metrics_table,
            recommendation=recommendation,
            processing_time=f"{processing_time:.2f} seconds"
        )
    except Exception as e:
        logger.error(f"Error in synchronous document analysis for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")



@app.get("/task/{task_id}", response_model=AnalysisStatus)
async def get_task_status_endpoint(task_id: str):
    """
    Check the status of a document analysis task.
    If completed, returns the analysis results, financial metrics table, recommendation, and processing time.
    """
    task_info = get_task_status(task_id)
    
    response = AnalysisStatus(task_id=task_id, status=task_info["status"])
    
    if task_info["status"] == "processing":
        logger.info(f"Task {task_id} is still processing")
    elif task_info["status"] == "failed":
        logger.error(f"Task {task_id} failed: {task_info.get('error', 'Unknown error')}")
        response.error = task_info.get("error", "Unknown error")
    else:
        logger.info(f"Task {task_id} completed")
        response.analysis_results = task_info.get("analysis_results", "")
        response.financial_metrics_table = task_info.get("financial_metrics_table", "")
        response.recommendation = task_info.get("recommendation", "")
        response.processing_time = task_info.get("processing_time", "")
    
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class SnapshotRequest(BaseModel):
    tickers: List[str]

@app.post("/snapshots")
async def get_snapshots(req: SnapshotRequest):
    """Return near real-time price snapshots for a list of tickers (1m interval).

    Body: { "tickers": ["AAPL","MSFT", ...] }
    Response: { "snapshots": [{ ticker, price, prev_close, change, change_percent }] }
    """
    try:
        svc = RealTimePriceService(ttl_seconds=10)
        return svc.get_snapshots([t.upper() for t in req.tickers[:50]])
    except Exception as e:
        logger.error(f"Error building snapshots: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to build snapshots: {str(e)}")

@app.websocket("/ws/prices")
async def prices_ws(websocket: WebSocket, tickers: str = Query("AAPL,MSFT"), interval: int = Query(5)):
    # Clients connect to: ws://host/ws/prices?tickers=AAPL,MSFT,TSLA&interval=5
    await manager.connect(websocket)
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()][:50]
    await stream_prices(websocket, ticker_list, interval_seconds=max(2, min(interval, 30)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)