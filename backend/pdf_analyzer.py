from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from PyPDF2 import PdfReader
import textwrap
import os

# ====== 1. PDF Text Extraction ======
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# ====== 2. Chunk Text (For Long Documents) ======
def chunk_text(text, chunk_size=1000):
    return textwrap.wrap(text, chunk_size)

# ====== 3. Load Quantized Mistral-7B (CPU-Friendly) ======
model_name = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
)

# Use pipeline for easier generation
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device="cpu",  # Force CPU
    torch_dtype=torch.float16,
)

# ====== 4. Process PDF & Generate Summary ======
def analyze_pdf(pdf_path, output_file="summary.txt"):
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    
    full_summary = ""
    for i, chunk in enumerate(chunks):
        prompt = f"Summarize this PDF text in detail:\n{chunk}"
        
        # Generate response (adjust max_length as needed)
        output = pipe(
            prompt,
            max_length=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        summary = output[0]['generated_text'].replace(prompt, "").strip()
        full_summary += f"\n\n=== Chunk {i+1} ===\n{summary}"
    
    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_summary)
    print(f"Summary saved to {output_file}")

# ====== RUN ======
if __name__ == "__main__":
    pdf_path = "hpl electric.pdf"  # Replace with your PDF path
    analyze_pdf(pdf_path)