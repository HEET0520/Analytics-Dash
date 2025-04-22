import os
from groq import Groq
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

class FinAnalyzerAgent:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
        logger.info(f"Groq API key loaded: {'Yes' if groq_api_key else 'No'}")
        if not self.groq_client:
            raise ValueError("Missing GROQ_API_KEY in .env file")

    def analyze_fundamentals(self, ticker, fundamentals, retries=3):
        logger.info(f"Analyzing fundamentals for {ticker}")
        if isinstance(fundamentals, str):
            return f"Error: {fundamentals}"

        metrics = {
            "Market Cap": fundamentals.get("marketCapitalization", "N/A"),
            "P/E Ratio": fundamentals.get("peTTM", "N/A"),
            "EPS": fundamentals.get("epsTTM", "N/A"),
            "Dividend Yield": fundamentals.get("dividendYieldTTM", "N/A"),
            "ROE": fundamentals.get("roeTTM", "N/A")
        }
        prompt = (
            f"Analyze the financial health of {ticker} based on the following metrics:\n"
            f"- Market Cap: {metrics['Market Cap']}M\n"
            f"- P/E Ratio: {metrics['P/E Ratio']}\n"
            f"- EPS: {metrics['EPS']}\n"
            f"- Dividend Yield: {metrics['Dividend Yield']}%\n"
            f"- ROE: {metrics['ROE']}%\n"
            "Provide a concise analysis (100-150 words) on valuation, profitability, and investment suitability."
        )
        for attempt in range(retries):
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=200
                )
                analysis = response.choices[0].message.content
                logger.info(f"Fundamentals analysis completed for {ticker}")
                return analysis
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return f"Error analyzing fundamentals for {ticker}."

if __name__ == "__main__":
    agent = FinAnalyzerAgent()
    fundamentals = {"marketCapitalization": 1000000, "peTTM": 25.5, "epsTTM": 2.1}
    print(agent.analyze_fundamentals("TSLA", fundamentals))