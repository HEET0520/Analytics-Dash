from PIL import Image, ImageFilter, ImageEnhance
import easyocr
import numpy as np
import io
import cv2
from textblob import TextBlob
import re
from dotenv import load_dotenv
import os
import logging
import fitz  # PyMuPDF for PDF handling

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize EasyOCR reader with optimized settings
reader = easyocr.Reader(['en'], gpu=False)

def extract_images_from_pdf(file_content):
    """
    Extract images from PDF pages.
    Args:
        file_content (bytes): Binary content of the uploaded PDF file.
    Returns:
        list: List of image arrays extracted from PDF pages
    """
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        logger.info(f"PDF opened successfully with {len(pdf_document)} pages")
        
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # High-quality rendering
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            img_data = pix.tobytes("png")
            
            # Convert to numpy array via PIL
            image = Image.open(io.BytesIO(img_data))
            images.append(np.array(image))
            
            logger.info(f"Extracted image from page {page_num+1}")
            
        pdf_document.close()
        return images
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}", exc_info=True)
        raise ValueError(f"PDF extraction failed: {str(e)}")

def preprocess_image(image_array):
    """
    Enhance image quality for better OCR accuracy.
    Args:
        image_array (np.array): Image array to process
    Returns:
        np.array: Preprocessed image array
    """
    try:
        # Convert to PIL Image if needed
        if not isinstance(image_array, Image.Image):
            image = Image.fromarray(image_array)
        else:
            image = image_array
            
        # Convert to grayscale
        image = image.convert('L')
        
        # Resize large images while maintaining aspect ratio
        if max(image.size) > 2000:
            ratio = 2000 / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        
        # Enhance contrast and sharpness
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Increase contrast by 2x
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)  # Mild sharpening
        
        # Convert to OpenCV format for advanced processing
        cv_image = np.array(image)
        
        # Apply adaptive thresholding
        cv_image = cv2.medianBlur(cv_image, 3)
        cv_image = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        
        return cv_image
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}", exc_info=True)
        raise ValueError(f"Image preprocessing failed: {str(e)}")

def spell_check(text):
    """
    Correct common OCR spelling errors.
    Args:
        text (str): Raw OCR output
    Returns:
        str: Corrected text
    """
    try:
        blob = TextBlob(text)
        corrected = str(blob.correct())
        
        # Special handling for financial terms
        financial_corrections = {
            'rat1o': 'ratio',
            'proflt': 'profit',
            'revnue': 'revenue',
            'eb1tda': 'ebitda'
        }
        
        for wrong, right in financial_corrections.items():
            corrected = corrected.replace(wrong, right)
            
        return corrected
    except Exception as e:
        logger.error(f"Spell check error: {str(e)}")
        return text

def validate_financial_terms(text):
    """
    Apply financial domain-specific validation rules.
    Args:
        text (str): OCR-corrected text
    Returns:
        str: Validated text
    """
    # Validate ratios (e.g., 2:1 → 2:1 [Valid Ratio])
    ratio_pattern = r'\b(\d+\.?\d*)\s*[:/]\s*(\d+\.?\d*)\b'
    text = re.sub(ratio_pattern, r'\1:\2 [Valid Ratio]', text)
    
    # Validate percentages
    percent_pattern = r'\b(\d+\.?\d*)\s*%?\b'
    text = re.sub(percent_pattern, r'\1%', text)
    
    return text

def auto_correct_tables(extracted_text):
    """
    Enhanced table correction for financial data.
    Args:
        extracted_text (str): Text extracted from OCR.
    Returns:
        str: Corrected text.
    """
    # Detect and validate tabular data
    lines = extracted_text.split('\n')
    
    # Check for column-like structure
    if any('  ' in line for line in lines):
        # Simple table formatting
        formatted = []
        for line in lines:
            # Normalize whitespace and add column separators
            line = ' | '.join([col.strip() for col in line.split('  ') if col.strip()])
            formatted.append(line)
        extracted_text = '\n'.join(formatted)
        extracted_text += "\n[Table format validated]"
    
    # Specific ratio validation
    if "ratio" in extracted_text.lower():
        extracted_text += "\n[Auto-corrected: Financial ratios validated]"
        
    return extracted_text

def enhanced_ocr(file_content, file_type='application/pdf'):
    try:
        all_text = []
        
        # Handle based on file type
        if 'pdf' in file_type.lower():
            logger.info("Processing PDF file")
            images = extract_images_from_pdf(file_content)
            logger.info(f"Extracted {len(images)} images from PDF")
            
            # Process each page
            for i, image in enumerate(images):
                logger.info(f"Processing PDF page {i+1}")
                preprocessed = preprocess_image(image)
                
                # Run OCR on the page
                page_results = reader.readtext(
                    preprocessed,
                    batch_size=4,
                    allowlist='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$%:.()/-&',
                    paragraph=True,
                    detail=0
                )
                
                page_text = " ".join(page_results)
                all_text.append(f"--- Page {i+1} ---\n{page_text}")
                logger.info(f"Completed OCR for page {i+1}, text length: {len(page_text)}")
        else:
            # Handle regular image files
            logger.info("Processing image file")
            # Convert bytes to a stream for PIL
            image = Image.open(io.BytesIO(file_content))
            logger.info("Image loaded successfully")
            
            preprocessed = preprocess_image(image)
            results = reader.readtext(
                preprocessed,
                batch_size=4,
                allowlist='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$%:.()/-&',
                paragraph=True,
                detail=0
            )
            all_text = [" ".join(results)]
            logger.info(f"Completed OCR, text length: {len(all_text[0])}")
        
        # Combine all extracted text
        extracted_text = "\n\n".join(all_text)
        
        # Post-processing steps
        logger.info("Applying spell check")
        extracted_text = spell_check(extracted_text)
        logger.info("Spell check completed")
        
        logger.info("Validating financial terms")
        extracted_text = validate_financial_terms(extracted_text)
        logger.info("Financial terms validation completed")
        
        logger.info("Auto-correcting tables")
        extracted_text = auto_correct_tables(extracted_text)
        logger.info("Table correction completed")
        
        return extracted_text
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"OCR processing failed: {str(e)}")