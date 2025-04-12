from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set")

print(f"Using HF_TOKEN: {HF_TOKEN[:5]}...")
try:
    model = pipeline(
        "text-generation",
        model="mistralai/Mistral-7B-Instruct-v0.3",
        token=HF_TOKEN,
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise