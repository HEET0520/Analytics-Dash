from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import google.generativeai as genai
import os
from google.api_core import exceptions
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import re
from fpdf import FPDF
import time
import pytesseract
import fitz  # Using PyMuPDF
import cv2
from io import BytesIO
import tempfile
from PIL import Image
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Initialize FastAPI app
app = FastAPI(title="Financial Document Analysis API")

# Add CORS middleware to allow requests from your custom website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your website domain(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyD-DLSBI8HFF7lFtnlazU4E81p8A40JIl4"
genai.configure(api_key=GEMINI_API_KEY)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:/Program Files/Tesseract-OCR/tessdata"

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

class PDF(FPDF):
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# Response model
class AnalysisResponse(BaseModel):
    analysis_results: str
    financial_metrics: str

class AnalysisStatus(BaseModel):
    task_id: str
    status: str
    
def extract_text_from_pdf(pdf_file_bytes):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def extract_images_from_pdf(pdf_file_bytes):
    images = []
    doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            images.append(image)
    return images

def extract_text_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    extracted_text = pytesseract.image_to_string(thresh)
    return extracted_text

def process_graphs(images):
    extracted_texts = [extract_text_from_image(img) for img in images]
    return "\n".join(extracted_texts)

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

    embeddings = model.encode(chunks, 
                              batch_size=32,
                              show_progress_bar=False,
                              convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    # Save FAISS index to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    faiss.write_index(index, temp_file.name)

    return temp_file.name, chunks  # Returning file path instead of index

def search_vector_db(query, index, chunks, k=3):
    """Retrieve the most relevant chunks from FAISS index."""
    query_vector = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    distances, indices = index.search(query_vector.astype(np.float32), k)
    
    retrieved_chunks = [chunks[i] for i in indices[0]]
    
    # Add metadata context
    metadata = "\n\n".join(retrieved_chunks)
    
    return metadata

def process_question(args):
    """Retrieve relevant financial data and pass it to Gemini API."""
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
            model_gen = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model_gen.generate_content(prompt)
            time.sleep(1)
            return f"### {question}\n{response.text if response and response.text else 'No relevant data found.'}"
        except exceptions.ResourceExhausted:
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            return f"### {question}\nError: {str(e)}"
    
    return f"### {question}\nError: Unable to process the question."

def extract_financial_metrics(text, retries=3):
    """Extract key financial metrics with retry mechanism"""
    metrics_prompt = """
    Extract and summarize the key financial information from this document.
    Include revenue, profit, growth rates, and any significant financial metrics.
    Present the information in a clear, structured format.
    """
    
    for attempt in range(retries):
        try:
            model_gen = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model_gen.generate_content(text + "\n" + metrics_prompt)
            time.sleep(1)  # Add delay between API calls
            return response.text
        except exceptions.ResourceExhausted:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return "Unable to extract metrics due to API limitations. Please try again later."
        except Exception as e:
            return f"Error extracting metrics: {str(e)}"

def analyze_report(text, graph_text=None):
    combined_text = text + "\n" + graph_text if graph_text else text
    index_path, chunks = create_vector_db(combined_text)

    # Load FAISS index from file
    index = faiss.read_index(index_path)

    prompt = ("Analyze the financial document and provide insights on key financial strengths, operational performance, "
              "growth trends, risks, and market positioning. Include relevant metrics, trends, and any notable observations "
              "that impact financial decision-making.")

    # Process the generalized analysis
    analysis_result = process_question((prompt, index, chunks))
    metrics = extract_financial_metrics(combined_text)

    # Clean up temporary file
    try:
        os.unlink(index_path)
    except:
        pass

    return analysis_result, metrics

# Task storage for background processing
task_results = {}


async def process_document_task(task_id: str, file_bytes: bytes, file_extension: str):
    try:
        if file_extension == "pdf":
            text = extract_text_from_pdf(file_bytes)
            images = extract_images_from_pdf(file_bytes)
            graph_text = process_graphs(images)
        else:  # Image files
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
        task_results[task_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.post("/analyze/", response_model=AnalysisStatus)
async def analyze_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Submit a financial document (PDF or image) for analysis.
    Returns a task ID that can be used to check the status of analysis.
    
    - **file**: Upload a PDF or image file
    """
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in ["pdf", "png", "jpg", "jpeg", "bmp", "gif", "tiff"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    file_bytes = await file.read()
    task_id = f"task_{int(time.time())}_{file.filename}"
    
    task_results[task_id] = {"status": "processing"}
    
    background_tasks.add_task(
        process_document_task,
        task_id,
        file_bytes,
        file_extension
    )
    
    return AnalysisStatus(task_id=task_id, status="processing")

@app.post("/analyze_sync/", response_model=AnalysisResponse)
async def analyze_document_sync(file: UploadFile = File(...)):
    """
    Analyze a financial document (PDF or image) and extract insights synchronously.
    This may take longer to respond but provides results in a single request.
    
    - **file**: Upload a PDF or image file
    """
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in ["pdf", "png", "jpg", "jpeg", "bmp", "gif", "tiff"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    contents = await file.read()
    
    if file_extension == "pdf":
        text = extract_text_from_pdf(contents)
        images = extract_images_from_pdf(contents)
        graph_text = process_graphs(images)
    else:  # Image files
        try:
            image = Image.open(BytesIO(contents))
            image_np = np.array(image)
            text = extract_text_from_image(image_np)
            graph_text = None
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    analysis_results, metrics = analyze_report(text, graph_text)
    
    return AnalysisResponse(
        analysis_results=analysis_results,
        financial_metrics=metrics
    )

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a document analysis task.
    If completed, returns the analysis results.
    """
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_results[task_id]
    
    if task_info["status"] == "processing":
        return {"status": "processing"}
    elif task_info["status"] == "failed":
        return {"status": "failed", "error": task_info.get("error", "Unknown error")}
    else:
        return {
            "status": "completed",
            "analysis_results": task_info["analysis_results"],
            "financial_metrics": task_info["financial_metrics"]
        }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)