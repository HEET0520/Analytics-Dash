import logging
from groq import Groq
from dotenv import load_dotenv
import os
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re
import time
import pytesseract
import fitz
import cv2
from io import BytesIO
import tempfile
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:/Program Files/Tesseract-OCR/tessdata"

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Grok client
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
if not groq_client:
    logger.error("GROQ_API_KEY not found in .env file")
    raise ValueError("GROQ_API_KEY not found in .env file")

# Task storage for background document processing
task_results = {}

def extract_text_from_pdf(pdf_file_bytes):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

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
        return extracted_text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

def process_graphs(images):
    extracted_texts = [extract_text_from_image(img) for img in images if img is not None]
    return "\n".join([text for text in extracted_texts if text])

def create_vector_db(_text, chunk_size=800):
    sentences = re.split(r'(?<=[.!?])\s+', _text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    faiss.write_index(index, temp_file.name)
    return temp_file.name, chunks

def search_vector_db(query, index, chunks, k=3):
    query_vector = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    distances, indices = index.search(query_vector.astype(np.float32), k)
    retrieved_chunks = [chunks[i] for i in indices[0]]
    return "\n\n".join(retrieved_chunks)

def process_question(args):
    question, index, chunks = args
    context = search_vector_db(question, index, chunks, k=3)
    
    prompt = f"""
    Question: {question}

    Information from document:
    {context}

    Provide a clear, concise answer based on the document information.
    Include specific numbers and metrics when available.
    """

    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                max_tokens=500,
                temperature=0.7
            )
            time.sleep(1)
            return f"### {question}\n{response.choices[0].message.content or 'No relevant data found.'}"
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for question '{question}': {str(e)}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return f"### {question}\nError: Unable to process the question: {str(e)}"

def extract_financial_metrics(text, retries=3):
    metrics_prompt = """
    Extract and summarize the key financial information from this document.
    Include revenue, profit, growth rates, and any significant financial metrics.
    Present the information in a clear, structured format.
    """
    
    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text + "\n" + metrics_prompt}],
                model="llama3-70b-8192",
                max_tokens=500,
                temperature=0.7
            )
            time.sleep(1)
            return response.choices[0].message.content or "No metrics extracted."
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for metrics extraction: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"Error extracting metrics: {str(e)}"

def analyze_report(text, graph_text=None):
    combined_text = text + "\n" + graph_text if graph_text else text
    index_path, chunks = create_vector_db(combined_text)
    index = faiss.read_index(index_path)

    prompt = (
        "Analyze the financial document and provide insights on key financial strengths, operational performance, "
        "growth trends, risks, and market positioning. Include relevant metrics, trends, and any notable observations "
        "that impact financial decision-making."
    )

    analysis_result = process_question((prompt, index, chunks))
    metrics = extract_financial_metrics(combined_text)

    try:
        os.unlink(index_path)
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {index_path}: {str(e)}")

    return analysis_result, metrics

async def process_document_task(task_id: str, file_bytes: bytes, file_extension: str):
    try:
        if file_extension == "pdf":
            text = extract_text_from_pdf(file_bytes)
            images = extract_images_from_pdf(file_bytes)
            graph_text = process_graphs(images)
        else:
            image = Image.open(BytesIO(file_bytes))
            image_np = np.array(image)
            text = extract_text_from_image(image_np)
            graph_text = None
        
        analysis_results, metrics = analyze_report(text, graph_text)
        
        task_results[task_id] = {
            "status": "completed",
            "analysis_results": analysis_results,
            "financial_metrics": metrics
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