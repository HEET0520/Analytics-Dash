from alpha_vantage.timeseries import TimeSeries
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pymc as pm
import numpy as np
from market_context import get_market_context
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set. Get one from https://huggingface.co/settings/tokens")
if not ALPHA_VANTAGE_KEY:
    raise ValueError("ALPHA_VANTAGE_KEY not set. Get one from https://www.alphavantage.co/support/#api-key")

print(f"Using HF_TOKEN: {HF_TOKEN[:5]}...")  # Debug: Masked token
print(f"Attempting to load model: google/flan-t5-small")  # Debug: Smaller model for CPU

# Set optimization parameters for Intel CPU
os.environ["OMP_NUM_THREADS"] = "4"  # Limit parallel threads for i5
os.environ["KMP_BLOCKTIME"] = "0"
os.environ["KMP_SETTINGS"] = "1"

# Initialize Alpha Vantage
ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format="pandas")

# Initialize model with CPU optimizations
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

def analyze_text(prompt, max_length=500):
    """
    Generate text analysis with FLAN-T5 small model.
    """
    # Prepare inputs (truncate if needed for 8GB RAM)
    inputs = tokenizer(prompt[:1000], return_tensors="pt", truncation=True, max_length=512)
    
    # Generate with conservative parameters for CPU
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            num_return_sequences=1,
            do_sample=False,  # Deterministic for faster CPU performance
            early_stopping=True
        )
    
    # Decode and return
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def fetch_stock_data(ticker):
    """
    Fetch 30-day stock price data.
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
    Returns:
        list: List of closing prices or error message.
    """
    try:
        data, _ = ts.get_daily(symbol=ticker, outputsize="compact")
        prices = data["4. close"].values
        return prices[-30:].tolist()
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

def analyze_stock(ticker, document_text=""):
    """
    Analyze stock based on prices, market context, and document text.
    Args:
        ticker (str): Stock ticker symbol.
        document_text (str): Optional document text for analysis.
    Returns:
        dict: Analysis results including trends, risks, and confidence.
    """
    stock_prices = fetch_stock_data(ticker)
    market_context = get_market_context(f"{ticker} stock news")
    prompt = (
        f"Analyze the stock {ticker} based on the following:\n"
        f"Recent 30-day closing prices: {stock_prices}\n"
        f"Market context: {market_context}\n"
        f"Document content (if any): {document_text[:300]}\n"  # Limit document text length
        "Identify 2 trends, 2 risks, and 1 investment opportunity."
    )
    analysis = analyze_text(prompt, max_length=500)
    confidence = calculate_confidence(stock_prices)
    return {
        "ticker": ticker,
        "analysis": analysis,
        "stock_prices": stock_prices,
        "confidence": confidence
    }

def calculate_confidence(prices):
    """
    Calculate confidence score using Bayesian inference.
    Args:
        prices (list): List of stock prices.
    Returns:
        float: Confidence score.
    """
    if isinstance(prices, str):  # Error case
        return 0.0
    
    # Use a simpler model with fewer samples for CPU efficiency
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=np.mean(prices), sigma=np.std(prices))
        sigma = pm.HalfNormal("sigma", sigma=10)
        pm.Normal("obs", mu=mu, sigma=sigma, observed=prices)
        # Reduce samples for faster processing on CPU
        trace = pm.sample(500, tune=200, chains=2, return_inferencedata=False)
    
    return float(np.mean(trace["mu"]) / np.max(prices))
