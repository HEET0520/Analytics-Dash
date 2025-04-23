import os
from celery import shared_task
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

@shared_task(bind=True)
def analyze_document(self, file_path, file_name):
    try:
        logger.info(f"Starting analysis for {file_name}")
        
        # Extract text based on file type
        text = extract_text(file_path, file_name)
        if not text:
            return {
                "status": "failed",
                "error": "Could not extract text from the document."
            }
        
        # Initialize Grok client
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {
                "status": "failed",
                "error": "GROQ_API_KEY not found in environment."
            }
        groq_client = Groq(api_key=groq_api_key)

        # Analyze the document using Grok
        prompt = (
            "You are a financial analyst. Analyze the following financial document and provide a detailed report. "
            "Include the following sections:\n"
            "- Summary: A brief overview of the document's key points.\n"
            "- Complete Analysis: A detailed analysis of the document's content, including financial strengths, weaknesses, and operational performance.\n"
            "- Financial Metrics: Key financial metrics extracted from the document (e.g., Revenue, EBITDA, Debt-to-Equity).\n"
            "- Key Insights: A list of 4-6 key insights from the analysis.\n"
            "- Sentiment: Determine the overall sentiment (positive, negative, or neutral) based on the document's content.\n"
            "- Recommendations: Provide 3-5 actionable investment recommendations.\n\n"
            f"Document content:\n{text[:4000]}"  # Limit to 4000 characters to avoid token limits
        )

        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=1000
        )
        analysis = response.choices[0].message.content

        # Parse the analysis into structured sections
        result = parse_analysis(analysis)
        result["status"] = "completed"
        logger.info(f"Analysis completed for {file_name}")
        return result

    except Exception as e:
        logger.error(f"Analysis failed for {file_name}: {str(e)}")
        return {
            "status": "failed",
            "error": f"Analysis failed: {str(e)}"
        }

def extract_text(file_path, file_name):
    ext = file_name.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        elif ext in ['doc', 'docx']:
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif ext in ['png', 'jpg', 'jpeg']:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        else:
            return ""
    except Exception as e:
        logger.error(f"Text extraction failed for {file_name}: {str(e)}")
        return ""

def parse_analysis(analysis):
    sections = {
        "summary": "",
        "analysis_results": "",
        "financial_metrics": "",
        "key_insights": [],
        "sentiment": "neutral",
        "recommendations": []
    }

    lines = analysis.split("\n")
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("- Summary:"):
            current_section = "summary"
            sections["summary"] = line.replace("- Summary:", "").strip()
        elif line.startswith("- Complete Analysis:"):
            current_section = "analysis_results"
            sections["analysis_results"] = line.replace("- Complete Analysis:", "").strip() + "\n"
        elif line.startswith("- Financial Metrics:"):
            current_section = "financial_metrics"
            sections["financial_metrics"] = line.replace("- Financial Metrics:", "").strip() + "\n"
        elif line.startswith("- Key Insights:"):
            current_section = "key_insights"
        elif line.startswith("- Sentiment:"):
            current_section = "sentiment"
            sentiment = line.replace("- Sentiment:", "").strip().lower()
            sections["sentiment"] = sentiment if sentiment in ["positive", "negative", "neutral"] else "neutral"
        elif line.startswith("- Recommendations:"):
            current_section = "recommendations"
        elif current_section == "summary":
            sections["summary"] += "\n" + line
        elif current_section == "analysis_results":
            sections["analysis_results"] += line + "\n"
        elif current_section == "financial_metrics":
            sections["financial_metrics"] += line + "\n"
        elif current_section == "key_insights" and line.startswith("-"):
            sections["key_insights"].append(line[1:].strip())
        elif current_section == "recommendations" and line.startswith("-"):
            sections["recommendations"].append(line[1:].strip())

    return sections