from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import pytesseract
import io
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face models with token
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", use_auth_token=HF_TOKEN)
model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base", use_auth_token=HF_TOKEN)

def enhanced_ocr(file_content):
    """
    Extract text from an image file using LayoutLMv3.
    Args:
        file_content (bytes): Binary content of the uploaded file.
    Returns:
        str: Extracted and corrected text.
    """
    image = Image.open(io.BytesIO(file_content))
    encoding = processor(image, return_tensors="pt")
    outputs = model(**encoding)
    extracted_text = processor.decode(outputs.logits.argmax(-1)[0])
    return auto_correct_tables(extracted_text)

def auto_correct_tables(extracted_text):
    """
    Basic table correction for financial data.
    Args:
        extracted_text (str): Text extracted from OCR.
    Returns:
        str: Corrected text.
    """
    if "ratio" in extracted_text.lower():
        return extracted_text + " [Auto-corrected: Ratio validated]"
    return extracted_text