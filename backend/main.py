from fastapi import FastAPI, UploadFile, File
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

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
print(f"HF_TOKEN loaded: {os.getenv('HF_TOKEN')[:5]}...")
# Initialize FastAPI and Redis
app = FastAPI()
redis_client = Redis(host="localhost", port=6379, db=0)

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
    """
    Process an uploaded document with OCR, RAG, and financial analysis.
    Args:
        file (UploadFile): Uploaded document file.
    Returns:
        dict: Extracted text, insights, market context, and RAG results.
    """
    cache_key = f"doc:{file.filename}"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    file_content = await file.read()
    extracted_text = enhanced_ocr(file_content)
    vector_db = setup_vector_db([extracted_text])
    insights = generate_insights(extracted_text)
    market_context = get_market_context()
    rag_results = query_rag("What are the key points?", vector_db)

    result = {
        "extracted_text": extracted_text,
        "insights": insights,
        "market_context": market_context,
        "rag_results": rag_results
    }
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result

@app.get("/query")
async def query_document(query: str):
    """
    Query the document database with a user question.
    Args:
        query (str): User query string.
    Returns:
        dict: Relevant document chunks.
    """
    vector_db = qdrant_client
    return {"results": query_rag(query, vector_db)}

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
    cache_key = f"stock:{ticker}"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    document_text = ""
    if file:
        file_content = await file.read()
        document_text = enhanced_ocr(file_content)

    result = analyze_stock(ticker, document_text)
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result