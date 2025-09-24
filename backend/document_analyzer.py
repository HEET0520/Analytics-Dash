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
import fitz
import pytesseract
import google.generativeai as genai
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from sklearn.cluster import KMeans
from joblib import Memory
from tabulate import tabulate

# Suppress TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:/Program Files/Tesseract-OCR/tessdata"

# Initialize models
model = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = None
try:
    # Use publicly accessible cross-encoder model
    cross_encoder_model = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    hf_token = os.getenv("HF_TOKEN")
    cross_encoder = CrossEncoder(cross_encoder_model, token=hf_token if hf_token else None)
    logger.info(f"Successfully loaded CrossEncoder: {cross_encoder_model}")
except Exception as e:
    logger.warning(f"Failed to load CrossEncoder: {str(e)}. Disabling reranking.")
    cross_encoder = None

memory = Memory("cache_dir", verbose=0)

# Initialize Gemini client
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.error("GEMINI_API_KEY not found in .env file")
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Task storage
task_results = {}

def extract_text_from_pdf(pdf_file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_images_from_pdf(pdf_file_bytes):
    images = []
    try:
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                if image is not None:
                    images.append(image)
        doc.close()
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}")
    return images

def extract_text_from_image(image):
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        extracted_text = pytesseract.image_to_string(thresh)
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

async def async_extract_text_from_image(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_text_from_image, image)

async def process_graphs(images):
    tasks = [async_extract_text_from_image(img) for img in images if img is not None]
    extracted_texts = await asyncio.gather(*tasks)
    return "\n".join([text for text in extracted_texts if text])

def semantic_chunking(text, model, max_chunk_size=800):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return [text]
    sentence_embeddings = model.encode(sentences, show_progress_bar=False)
    num_clusters = max(1, len(sentences) // 5)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(sentence_embeddings)
    
    chunks = []
    current_chunk, current_label = "", None
    for sentence, label in zip(sentences, labels):
        if current_label != label or len(current_chunk) + len(sentence) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_label = label
        else:
            current_chunk += " " + sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def async_encode_batch(batch, model):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model.encode, batch, False, True)

async def create_vector_db(text, chunk_size=800, max_iterations=2):
    for iteration in range(max_iterations):
        chunks = semantic_chunking(text, model, chunk_size=chunk_size)
        if not chunks:
            logger.warning("No chunks created, returning empty index")
            return None, []
        
        batch_size = 32
        tasks = [async_encode_batch(chunks[i:i+batch_size], model) for i in range(0, len(chunks), batch_size)]
        embeddings = await asyncio.gather(*tasks)
        embeddings = np.vstack(embeddings)
        
        dimension = embeddings.shape[1]
        if len(chunks) < 100:
            index = faiss.IndexFlatL2(dimension)
        else:
            nlist = min(100, len(chunks) // 2)
            m = 8
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, 8)
            index.train(embeddings.astype(np.float32))
        
        index.add(embeddings.astype(np.float32))
        
        test_query = "What are the main financial highlights?"
        query_vector = model.encode([test_query], show_progress_bar=False, convert_to_numpy=True)
        distances, _ = index.search(query_vector.astype(np.float32), min(5, len(chunks)))
        avg_distance = np.mean(distances[0]) if distances[0].size > 0 else float('inf')
        
        if avg_distance < 0.5 or iteration == max_iterations - 1:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.faiss')
            faiss.write_index(index, temp_file.name)
            return temp_file.name, chunks
        
        chunk_size = int(chunk_size * 0.9)
    
    logger.warning("Max iterations reached without satisfactory index")
    return None, chunks

def search_vector_db(query, index, chunks, k=5):
    if not chunks or not index:
        return ""
    
    query_vector = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    candidate_k = min(k * 3, len(chunks))
    dense_distances, dense_indices = index.search(query_vector.astype(np.float32), candidate_k)
    retrieved_chunks = [chunks[i] for i in dense_indices[0]]
    
    tokenized_chunks = [chunk.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    max_dense_distance = max(dense_distances[0]) if dense_distances[0].size > 0 else 1
    dense_scores = [1 - (d / max_dense_distance) for d in dense_distances[0]]
    hybrid_scores = {}
    for idx, dense_score in zip(dense_indices[0], dense_scores):
        hybrid_scores[idx] = 0.7 * dense_score + 0.3 * bm25_scores[idx]
    
    top_k_indices = sorted(hybrid_scores.keys(), key=lambda x: hybrid_scores[x], reverse=True)[:candidate_k]
    top_chunks = [chunks[i] for i in top_k_indices]
    
    if cross_encoder:
        batch_size = 16
        pairs = [[query, chunk] for chunk in top_chunks]
        scores = []
        for i in range(0, len(pairs), batch_size):
            batch_scores = cross_encoder.predict(pairs[i:i+batch_size])
            scores.extend(batch_scores)
        ranked_indices = np.argsort(scores)[::-1][:k]
        final_chunks = [top_chunks[i] for i in ranked_indices]
    else:
        final_chunks = top_chunks[:k]  # Fallback to hybrid scores without reranking
    
    return "\n\n".join(final_chunks)

@memory.cache
def cached_generate_content(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text if response.text else ""
    except Exception as e:
        logger.error(f"Error in cached_generate_content: {str(e)}")
        raise

def compute_confidence(response_text, question):
    has_numbers = bool(re.search(r'\d+', response_text))
    length_score = min(len(response_text) / 500, 1.0)
    question_keywords = set(question.lower().split())
    response_keywords = set(response_text.lower().split())
    keyword_overlap = len(question_keywords.intersection(response_keywords)) / max(len(question_keywords), 1)
    return 0.5 * length_score + 0.3 * (1 if has_numbers else 0) + 0.2 * keyword_overlap

async def process_question(args, max_attempts=2):
    question, index, chunks = args
    attempt = 0
    chunk_size = 800
    current_text = "\n".join(chunks)
    
    while attempt < max_attempts:
        context = search_vector_db(question, index, chunks, k=5)
        prompt = f"""
        Question: {question}
        Information from document:
        {context}
        Provide a clear, concise answer based on the document information.
        Include specific numbers and metrics when available.
        """
        try:
            response_text = cached_generate_content(prompt)
            confidence = compute_confidence(response_text, question)
            if confidence > 0.7 or attempt == max_attempts - 1:
                return f"### {question}\n{response_text if response_text else 'No relevant data found.'}"
            chunk_size = int(chunk_size * 0.8)
            index_path, chunks = await create_vector_db(current_text, chunk_size=chunk_size)
            index = faiss.read_index(index_path) if index_path else None
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for question '{question}': {str(e)}")
            if attempt == max_attempts - 1:
                return f"### {question}\nError: Unable to process the question: {str(e)}"
        attempt += 1
    return f"### {question}\nError: Max attempts reached"

def extract_financial_metrics_table(text, retries=3):
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
    
    for attempt in range(retries):
        try:
            response = gemini_model.generate_content(text + "\n" + metrics_prompt)
            json_match = re.search(r'\{[\s\S]*\}', response.text)
            if json_match:
                json_str = json_match.group(0)
                try:
                    metrics_data = eval(json_str)
                    if not isinstance(metrics_data, dict):
                        raise ValueError("Parsed data is not a dictionary")
                    metrics_table = [[key, value] for key, value in metrics_data.items()]
                    return tabulate(metrics_table, headers=["Metric", "Value"], tablefmt="grid"), metrics_data
                except Exception as e:
                    logger.warning(f"Failed to parse metrics JSON: {e}")
            logger.warning("No JSON found in response")
            return "No financial metrics extracted.", {}
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for metrics extraction: {str(e)}")
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return f"Error extracting metrics: {str(e)}", {}

def generate_buy_sell_recommendation(text, metrics_data):
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
    
    for attempt in range(3):
        try:
            response = gemini_model.generate_content(text + "\n" + recommendation_prompt)
            return response.text if response.text else "Unable to generate recommendation due to insufficient data."
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for recommendation generation: {str(e)}")
            if attempt < 2:
                time.sleep(1)
            else:
                return f"Error generating recommendation: {str(e)}"

async def analyze_report(text, graph_text=None):
    start_time = time.time()
    combined_text = text + "\n" + graph_text if graph_text else text
    
    index_path, chunks = await create_vector_db(combined_text)
    index = faiss.read_index(index_path) if index_path else None
    
    questions = [
        "What are the main financial highlights and performance indicators?",
        "What are the major growth trends and areas of improvement?",
        "What are the key risks and challenges mentioned?"
    ]
    
    tasks = [process_question((q, index, chunks)) for q in questions]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    metrics_table, metrics_data = extract_financial_metrics_table(combined_text)
    recommendation = generate_buy_sell_recommendation(combined_text, metrics_data)
    
    analysis_result = "\n\n".join([str(r) for r in results if not isinstance(r, Exception)])
    
    if index_path:
        try:
            os.unlink(index_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {index_path}: {str(e)}")
    
    processing_time = time.time() - start_time
    logger.info(f"Report analysis completed in {processing_time:.2f} seconds")
    
    return analysis_result, metrics_table, recommendation, processing_time

async def process_document_task(task_id: str, file_bytes: bytes, file_extension: str):
    try:
        start_time = time.time()
        if file_extension.lower() == "pdf":
            text = extract_text_from_pdf(file_bytes)
            images = extract_images_from_pdf(file_bytes)
            graph_text = await process_graphs(images)
        else:
            image = Image.open(BytesIO(file_bytes))
            image_np = np.array(image)
            text = extract_text_from_image(image_np)
            graph_text = None
        
        analysis_results, metrics_table, recommendation, proc_time = await analyze_report(text, graph_text)
        
        task_results[task_id] = {
            "status": "completed",
            "analysis_results": analysis_results,
            "financial_metrics_table": metrics_table,
            "recommendation": recommendation,
            "processing_time": f"{proc_time:.2f} seconds",
            "completion_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Document processing failed for task {task_id}: {str(e)}")
        task_results[task_id] = {
            "status": "failed",
            "error": str(e)
        }

def get_task_status(task_id: str):
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_results[task_id]