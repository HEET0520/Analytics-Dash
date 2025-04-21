from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ocr_processor import enhanced_ocr
from rag_system import setup_vector_db, query_rag, qdrant_client
from fin_analyzer import generate_insights
from market_context import get_market_context
from stock_analyzer import analyze_stock
from redis import Redis
import json
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    logger.warning("HF_TOKEN not set! Please set up your Hugging Face token")

# Initialize FastAPI and Redis
app = FastAPI()
try:
    redis_client = Redis(host="localhost", port=6379, db=0)
    redis_client.ping()  # Test connection
    redis_available = True
    logger.info("Redis successfully connected")
except Exception as e:
    redis_available = False
    logger.warning(f"Redis unavailable, continuing without caching: {e}")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_document")
async def process_document(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}, size: {file.size}, content_type: {file.content_type}")
    if redis_available:
        cache_key = f"doc:{file.filename}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info("Returning cached result")
            return json.loads(cached_result)

    try:
        logger.info("Reading file content")
        file_content = await file.read()
        logger.info(f"File content read, size: {len(file_content)} bytes")
        
        logger.info(f"Running OCR on file: {file.filename}")
        # Pass the content type to enhanced_ocr
        extracted_text = enhanced_ocr(file_content, file.content_type)
        logger.info(f"OCR completed, extracted text length: {len(extracted_text)}")
        
        logger.info("Setting up vector database")
        vector_db = setup_vector_db([extracted_text])
        logger.info("Vector database setup completed")
        
        logger.info("Generating insights")
        insights = generate_insights(extracted_text)
        logger.info("Insights generated")
        
        logger.info("Getting market context")
        market_context = get_market_context()
        logger.info("Market context retrieved")
        
        logger.info("Querying RAG system")
        rag_results = query_rag("What are the key points?", vector_db)
        logger.info("RAG query completed")

        result = {
            "extracted_text": extracted_text,
            "insights": insights,
            "market_context": market_context,
            "rag_results": rag_results
        }
        
        if redis_available:
            logger.info("Caching result")
            redis_client.setex(cache_key, 3600, json.dumps(result))
            
        return result
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/query")
async def query_document(query: str):
    """
    Query the document database with a user question.
    Args:
        query (str): User query string.
    Returns:
        dict: Relevant document chunks.
    """
    try:
        vector_db = qdrant_client
        return {"results": query_rag(query, vector_db)}
    except Exception as e:
        logger.error(f"Error querying document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying document: {str(e)}")

@app.post("/analyze_stock")
async def analyze_stock_endpoint(ticker: str, file: UploadFile = None):
    """
    Analyze a stock with optional document input.
    Args:
        ticker (str): Stock ticker symbol.
        file (UploadFile, optional): Uploaded document file.
    Returns:
        dict: Stock analysis results.
    """
    # Check cache if Redis available
    if redis_available:
        cache_key = f"stock:{ticker}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

    try:
        document_text = ""
        if file:
            file_content = await file.read()
            # Pass the content type to enhanced_ocr
            document_text = enhanced_ocr(file_content, file.content_type)

        result = analyze_stock(ticker, document_text)
        
        # Store in cache if Redis available
        if redis_available:
            redis_client.setex(cache_key, 3600, json.dumps(result))
            
        return result
    except Exception as e:
        logger.error(f"Error analyzing stock: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing stock: {str(e)}")

@app.get("/healthcheck")
async def healthcheck():
    """Simple endpoint to check if the API is running"""
    return {"status": "ok", "redis": redis_available}