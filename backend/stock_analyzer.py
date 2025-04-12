from alpha_vantage.timeseries import TimeSeries
from transformers import pipeline
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
    raise ValueError("HF_TOKEN is not set in environment or .env file")
print(f"Using HF_TOKEN: {HF_TOKEN[:5]}...")  # Debug: Masked token
print(f"Attempting to load model: mistralai/Mistral-7B-Instruct-v0.3")  # Debug

# Initialize Alpha Vantage
ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format="pandas")

# Initialize Hugging Face pipeline
try:
    stock_analyzer = pipeline(
        "text-generation",
        model="mistralai/Mistral-7B-Instruct-v0.3",
        device_map="auto",
        torch_dtype=torch.bfloat16,
        token=HF_TOKEN,  # Use 'token' instead of 'use_auth_token'
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise

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
        f"Document content (if any): {document_text}\n"
        "Identify 2 trends, 2 risks, and 1 investment opportunity."
    )
    result = stock_analyzer(prompt, max_length=500, num_return_sequences=1)
    analysis = result[0]["generated_text"]
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
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=np.mean(prices), sigma=np.std(prices))
        sigma = pm.HalfNormal("sigma", sigma=10)
        pm.Normal("obs", mu=mu, sigma=sigma, observed=prices)
        trace = pm.sample(1000, tune=500, return_inferencedata=False)
    return float(np.mean(trace["mu"]) / np.max(prices))