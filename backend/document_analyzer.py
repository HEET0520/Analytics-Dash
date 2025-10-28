import logging
import os
import re
import time
import tempfile
import numpy as np
import pandas as pd
import faiss
import cv2
import asyncio
import concurrent.futures
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import PyPDF2
# import fitz  # pyright: ignore[reportMissingImports]
import pytesseract
import google.generativeai as genai
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from joblib import Memory
from tabulate import tabulate

# Suppress TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:/Program Files/Tesseract-OCR/tessdata"
logger.info("Tesseract configured")

# Initialize models with ONNX backend for speed
logger.info("Initializing SentenceTransformer model with ONNX backend...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2', backend="onnx")
    logger.info("SentenceTransformer ONNX model initialized successfully")
except Exception as e:
    logger.warning(f"ONNX backend failed, falling back to PyTorch: {e}")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    if model.device.type == 'cuda':
        model.half()

# Disable CrossEncoder for speed (optional - enable if you need reranking)
cross_encoder = None
logger.info("CrossEncoder disabled for speed optimization")

memory = Memory("cache_dir", verbose=0)
logger.info("Memory cache initialized")

# Initialize Gemini client
logger.info("Initializing Gemini client...")
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.error("GEMINI_API_KEY not found in .env file")
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")
logger.info("Gemini client initialized successfully")

# Task storage
task_results = {}

def extract_text_from_pdf(pdf_file_bytes):
    logger.info("Starting PDF text extraction")
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
        logger.info(f"PDF loaded, number of pages: {len(pdf_reader.pages)}")
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        logger.info(f"PDF text extraction completed. Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        raise

def extract_images_from_pdf(pdf_file_bytes):
    logger.info("Starting PDF image extraction")
    images = []
    try:
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
        logger.info(f"PDF opened for image extraction, pages: {len(doc)}")
        # Limit to first 5 pages for speed
        max_pages = min(5, len(doc))
        for page_num in range(max_pages):
            page = doc[page_num]
            for img_num, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                if image is not None:
                    images.append(image)
        doc.close()
        logger.info(f"PDF image extraction completed. Extracted {len(images)} images")
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}", exc_info=True)
    return images

def extract_text_from_image(image):
    logger.debug("Starting OCR text extraction from image")
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        extracted_text = pytesseract.image_to_string(thresh)
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}", exc_info=True)
        return ""

async def async_extract_text_from_image(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_text_from_image, image)

async def process_graphs(images):
    logger.info(f"Starting graph processing for {len(images)} images")
    # Process only first 3 images to save time
    images_to_process = images[:3]
    tasks = [async_extract_text_from_image(img) for img in images_to_process if img is not None]
    extracted_texts = await asyncio.gather(*tasks)
    combined_text = "\n".join([text for text in extracted_texts if text])
    logger.info(f"Graph processing completed. Extracted {len(combined_text)} characters")
    return combined_text

def _ensure_str(s):
    """Return s if it's a str, otherwise return empty string."""
    if s is None:
        return ""
    if isinstance(s, bool):
        return str(s)
    if isinstance(s, str):
        return s
    return str(s)

def simple_semantic_chunking(text, chunk_size=600):
    """
    Fast chunking based on sentence boundaries without clustering overhead.
    """
    logger.info(f"Starting simple semantic chunking with chunk_size={chunk_size}")
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    logger.info(f"Text split into {len(sentences)} sentences")
    
    if not sentences:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    logger.info(f"Simple chunking completed. Created {len(chunks)} chunks")
    return chunks

async def create_vector_db(text, chunk_size=600):
    logger.info(f"Creating vector DB with chunk_size={chunk_size}")
    
    chunks = simple_semantic_chunking(text, chunk_size=chunk_size)
    if not chunks:
        logger.warning("No chunks created, returning empty index")
        return None, [], None
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Single large batch encoding
    logger.info("Encoding all chunks in batches...")
    embeddings = model.encode(chunks, batch_size=64, show_progress_bar=False, convert_to_numpy=True)
    logger.info(f"All chunks encoded, embeddings shape: {embeddings.shape}")
    
    dimension = embeddings.shape[1]
    logger.info(f"Creating FAISS index with dimension={dimension}")
    
    # Always use IndexFlatL2 for speed
    index = faiss.IndexFlatL2(dimension)
    logger.info("Using IndexFlatL2 for fastest search")
    
    logger.info("Adding embeddings to FAISS index...")
    index.add(embeddings.astype(np.float32))
    logger.info(f"FAISS index created with {index.ntotal} vectors")
    
    # Pre-compute BM25 index once
    logger.info("Creating BM25 index...")
    tokenized_chunks = [chunk.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    logger.info("BM25 index created")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.faiss')
    faiss.write_index(index, temp_file.name)
    logger.info(f"FAISS index saved to temporary file: {temp_file.name}")
    
    return temp_file.name, chunks, bm25

def search_vector_db(query, index, chunks, bm25, k=5):
    logger.info(f"Searching vector DB for query: '{query}' with k={k}")
    
    if not chunks or not index:
        logger.warning("Empty chunks or no index, returning empty result")
        return ""
    
    logger.info("Encoding query...")
    query_vector = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    
    # Get more candidates for hybrid reranking
    candidate_k = min(k * 2, len(chunks))
    logger.info(f"Searching for top {candidate_k} candidates")
    dense_distances, dense_indices = index.search(query_vector.astype(np.float32), candidate_k)
    
    # BM25 scoring (using pre-computed index)
    logger.info("Computing BM25 scores...")
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    logger.info("BM25 scoring completed")
    
    # Hybrid scoring: 70% dense, 30% BM25
    logger.info("Computing hybrid scores...")
    max_dense_distance = max(dense_distances[0]) if dense_distances[0].size > 0 else 1
    dense_scores = [1 - (d / max_dense_distance) for d in dense_distances[0]]
    
    hybrid_scores = {}
    for idx, dense_score in zip(dense_indices[0], dense_scores):
        hybrid_scores[idx] = 0.7 * dense_score + 0.3 * bm25_scores[idx]
    
    logger.info(f"Hybrid scores computed for {len(hybrid_scores)} results")
    
    # Get top k results
    top_k_indices = sorted(hybrid_scores.keys(), key=lambda x: hybrid_scores[x], reverse=True)[:k]
    final_chunks = [chunks[i] for i in top_k_indices]
    
    result = "\n\n".join(final_chunks)
    logger.info(f"Search completed, returning {len(result)} characters")
    return result

@memory.cache
def cached_generate_content(prompt):
    logger.info("Calling Gemini API (cached_generate_content)")
    
    try:
        prompt_str = _ensure_str(prompt)
        logger.info("Sending request to Gemini model...")
        response = gemini_model.generate_content(prompt_str)
        logger.info("Received response from Gemini model")
        
        result = response.text if response.text else ""
        return result
    except Exception as e:
        logger.error(f"Error in cached_generate_content: {str(e)}", exc_info=True)
        raise

async def process_question(args):
    question, index, chunks, bm25 = args
    logger.info(f"Processing question: '{question}'")
    
    logger.info("Searching vector DB for relevant context...")
    context = search_vector_db(question, index, chunks, bm25, k=5)
    logger.info(f"Context retrieved, length: {len(context)}")
    
    prompt = f"""
    Question: {question}
    Information from document:
    {context}
    Provide a clear, concise answer based on the document information.
    Include specific numbers and metrics when available.
    """
    
    try:
        logger.info("Generating content with Gemini...")
        response_text = cached_generate_content(prompt)
        logger.info(f"Content generated, response length: {len(response_text)}")
        return f"### {question}\n{response_text if response_text else 'No relevant data found.'}"
    except Exception as e:
        logger.error(f"Failed for question '{question}': {str(e)}", exc_info=True)
        return f"### {question}\nError: Unable to process the question: {str(e)}"

def extract_financial_metrics_table(text):
    logger.info("Extracting financial metrics table")
    
    metrics_prompt = """
    Extract all key financial metrics from this document including but not limited to:
    - Revenue (current and previous period)
    - Net Income/Profit (current and previous period)
    - EPS (Earnings Per Share)
    - EBITDA
    - Profit Margin
    - ROE (Return on Equity)
    - ROA (Return on Assets)
    - Debt-to-Equity Ratio
    - Current Ratio
    - Operating Cash Flow
    - Growth Rates (YoY)
    
    Format the output EXACTLY as a JSON object with metric names as keys and values as numbers or strings with units.
    Example:
    {
      "Revenue": "$1.2B (2023), $1.1B (2022)",
      "Net Income": "$240M (2023), $220M (2022)",
      "YoY Revenue Growth": "9.1%",
      "EPS": "$1.45 (2023), $1.30 (2022)"
    }
    
    Include period indicators (quarters, years) and percent changes when available.
    If no metrics are found, return an empty JSON object {}.
    """
    
    try:
        safe_text = _ensure_str(text)
        # Limit text length for faster processing
        combined_prompt = safe_text[:8000] + "\n" + metrics_prompt
        
        logger.info("Sending metrics extraction request to Gemini...")
        response = gemini_model.generate_content(combined_prompt)
        logger.info("Received metrics extraction response")
        
        json_match = re.search(r'\{[\s\S]*\}', response.text)
        if json_match:
            json_str = json_match.group(0)
            try:
                metrics_data = eval(json_str)
                if not isinstance(metrics_data, dict):
                    raise ValueError("Parsed data is not a dictionary")
                logger.info(f"Successfully parsed metrics: {len(metrics_data)} items")
                metrics_table = [[key, value] for key, value in metrics_data.items()]
                table_result = tabulate(metrics_table, headers=["Metric", "Value"], tablefmt="grid")
                logger.info("Metrics table created successfully")
                return table_result, metrics_data
            except Exception as e:
                logger.warning(f"Failed to parse metrics JSON: {e}")
        
        return "No financial metrics extracted.", {}
    except Exception as e:
        logger.error(f"Metrics extraction failed: {str(e)}", exc_info=True)
        return f"Error extracting metrics: {str(e)}", {}

def generate_buy_sell_recommendation(text, metrics_data):
    logger.info("Generating buy/sell recommendation")
    
    recommendation_prompt = f"""
    Based on the financial document and the following metrics:
    
    {metrics_data}
    
    Provide a clear BUY, SELL, or HOLD recommendation with a confidence score (1-10).
    Include a brief justification (3-5 bullet points) highlighting key factors supporting this recommendation.
    Format your response as follows:
    
    RECOMMENDATION: [BUY/SELL/HOLD]
    CONFIDENCE: [1-10]
    
    JUSTIFICATION:
    • [Point 1]
    • [Point 2]
    • [Point 3]
    
    KEY RISKS:
    • [Risk 1]
    • [Risk 2]
    
    If no recommendation can be made, return "Unable to generate recommendation due to insufficient data."
    """
    
    try:
        safe_text = _ensure_str(text)
        # Limit text length for faster processing
        combined_prompt = safe_text[:6000] + "\n" + recommendation_prompt
        
        logger.info("Sending recommendation request to Gemini...")
        response = gemini_model.generate_content(combined_prompt)
        logger.info("Received recommendation response")
        
        result = response.text if response.text else "Unable to generate recommendation due to insufficient data."
        logger.info(f"Recommendation generated, length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}", exc_info=True)
        return f"Error generating recommendation: {str(e)}"

async def analyze_report(text, graph_text=None):
    logger.info("="*80)
    logger.info("Starting report analysis")
    logger.info("="*80)
    start_time = time.time()
    
    logger.info("Converting inputs to strings...")
    safe_text = _ensure_str(text)
    safe_graph = _ensure_str(graph_text)
    
    logger.info("Combining text and graph data...")
    if not safe_graph:
        combined_text = safe_text
    elif not safe_text:
        combined_text = safe_graph
    else:
        combined_text = safe_text + "\n" + safe_graph
    
    logger.info(f"Combined text length: {len(combined_text)}")
    
    # Create vector DB with BM25
    logger.info("Creating vector database with BM25...")
    index_path, chunks, bm25 = await create_vector_db(combined_text)
    logger.info(f"Vector database created")
    
    index = faiss.read_index(index_path) if index_path else None
    
    questions = [
        "What are the main financial highlights and performance indicators?",
        "What are the major growth trends and areas of improvement?",
        "What are the key risks and challenges mentioned?"
    ]
    logger.info(f"Processing {len(questions)} questions")
    
    # Process all questions in parallel
    tasks = [process_question((q, index, chunks, bm25)) for q in questions]
    logger.info("Executing question processing tasks in parallel...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All question processing tasks completed")
    
    # Extract metrics and generate recommendation
    logger.info("Extracting financial metrics and generating recommendation...")
    metrics_table, metrics_data = extract_financial_metrics_table(combined_text)
    recommendation = generate_buy_sell_recommendation(combined_text, metrics_data)
    logger.info("Metrics and recommendation completed")
    
    logger.info("Compiling analysis results...")
    analysis_result = "\n\n".join([str(r) for r in results if not isinstance(r, Exception)])
    
    if index_path:
        try:
            os.unlink(index_path)
            logger.info(f"Temporary index file deleted")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {str(e)}")
    
    processing_time = time.time() - start_time
    logger.info("="*80)
    logger.info(f"Report analysis completed in {processing_time:.2f} seconds")
    logger.info("="*80)
    
    return analysis_result, metrics_table, recommendation, processing_time

async def process_document_task(task_id: str, file_bytes: bytes, file_extension: str):
    logger.info("="*80)
    logger.info(f"Starting document processing task: {task_id}")
    logger.info(f"File extension: {file_extension}, file size: {len(file_bytes)} bytes")
    logger.info("="*80)
    
    try:
        start_time = time.time()
        
        if file_extension.lower() == "pdf":
            logger.info("Processing PDF document")
            # Extract text and images in parallel
            text_task = asyncio.get_event_loop().run_in_executor(None, extract_text_from_pdf, file_bytes)
            images_task = asyncio.get_event_loop().run_in_executor(None, extract_images_from_pdf, file_bytes)
            
            text, images = await asyncio.gather(text_task, images_task)
            logger.info(f"PDF processing completed")
            
            logger.info("Processing graphs from images...")
            graph_text = await process_graphs(images)
            logger.info(f"Graph text extracted, length: {len(graph_text)}")
        else:
            logger.info(f"Processing image document ({file_extension})")
            image = Image.open(BytesIO(file_bytes))
            image_np = np.array(image)
            logger.info(f"Image loaded, shape: {image_np.shape}")
            
            text = extract_text_from_image(image_np)
            logger.info(f"Text extracted from image, length: {len(text)}")
            graph_text = None
        
        logger.info("Starting report analysis...")
        analysis_results, metrics_table, recommendation, proc_time = await analyze_report(text, graph_text)
        logger.info("Report analysis completed successfully")
        
        task_results[task_id] = {
            "status": "completed",
            "analysis_results": analysis_results,
            "financial_metrics_table": metrics_table,
            "recommendation": recommendation,
            "processing_time": f"{proc_time:.2f} seconds",
            "completion_time": time.time() - start_time
        }
        
        logger.info("="*80)
        logger.info(f"Document processing task {task_id} completed successfully")
        logger.info(f"Total completion time: {time.time() - start_time:.2f} seconds")
        logger.info("="*80)
        
    except Exception as e:
        logger.error("="*80)
        logger.error(f"Document processing FAILED for task {task_id}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("="*80)
        logger.error("Full traceback:", exc_info=True)
        
        task_results[task_id] = {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }

def get_task_status(task_id: str):
    logger.info(f"Getting status for task: {task_id}")
    if task_id not in task_results:
        logger.warning(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = task_results[task_id]
    logger.info(f"Task {task_id} status: {status.get('status', 'unknown')}")
    return status
