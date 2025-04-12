from transformers import pipeline
import torch
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set in environment or .env file")

print(f"Using HF_TOKEN: {HF_TOKEN[:5]}...")  # Debug: Masked token
print(f"Attempting to load model: mistralai/Mistral-7B-Instruct-v0.3")  # Debug
try:
    fin_analyzer = pipeline(
        "text-generation",
        model="mistralai/Mistral-7B-Instruct-v0.3",
        device_map="auto",
        torch_dtype=torch.bfloat16,
        token=HF_TOKEN,
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise

def generate_insights(text):
    """Generate insights from input text using the fin_analyzer pipeline."""
    if not hasattr(generate_insights, 'initialized'):
        raise RuntimeError("fin_analyzer not initialized properly")
    result = fin_analyzer(text, max_length=100, num_return_sequences=1)
    return result[0]['generated_text']  # Adjust based on pipeline output