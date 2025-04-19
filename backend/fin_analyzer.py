from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set. Get one from https://huggingface.co/settings/tokens")

print(f"Using HF_TOKEN: {HF_TOKEN[:5]}...")  # Debug: Masked token
print(f"Attempting to load model: google/flan-t5-small")  # Debug: Smaller model for CPU

# Set optimization parameters for Intel CPU
os.environ["OMP_NUM_THREADS"] = "4"  # Limit parallel threads for i5
os.environ["KMP_BLOCKTIME"] = "0"
os.environ["KMP_SETTINGS"] = "1"

# Load tokenizer and model with optimizations for CPU efficiency
try:
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small", token=HF_TOKEN)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        "google/flan-t5-small", 
        device_map="cpu",  # Force CPU
        low_cpu_mem_usage=True,  # Optimize for low memory
        token=HF_TOKEN
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise

def generate_insights(text):
    """Generate insights from input text using FLAN-T5 small."""
    # Initialize the 'initialized' attribute on first call
    if not hasattr(generate_insights, 'initialized'):
        generate_insights.initialized = True
    
    # Prepare inputs (truncate if needed for 8GB RAM)
    inputs = tokenizer(text[:1000], return_tensors="pt", truncation=True, max_length=512)
    
    # Generate with conservative parameters for CPU
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=100,
            num_return_sequences=1,
            do_sample=False,  # Deterministic for faster CPU performance
            early_stopping=True
        )
    
    # Decode and return
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result