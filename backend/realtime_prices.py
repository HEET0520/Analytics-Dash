import yfinance as yf
from cachetools import TTLCache
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RealTimePriceService:
    """Fetch near real-time prices for a list of tickers.

    Uses yfinance 1-minute data for the current day and falls back gracefully.
    Caches results briefly (default 10s) to avoid hammering upstream.
    """

    def __init__(self, ttl_seconds: int = 10):
        self.cache = TTLCache(maxsize=128, ttl=ttl_seconds)

    def _latest_price_1m(self, ticker: str):
        try:
            hist = yf.Ticker(ticker).history(period="1d", interval="1m")
            if hist is None or hist.empty:
                return None
            close = hist["Close"].dropna()
            return float(close.iloc[-1]) if len(close) else None
        except Exception as e:
            logger.error(f"1m price fetch failed for {ticker}: {e}")
            return None

    def _prev_close(self, ticker: str):
        try:
            daily = yf.Ticker(ticker).history(period="2d", interval="1d")
            if daily is None or daily.empty:
                return None
            close = daily["Close"].dropna()
            if len(close) >= 2:
                return float(close.iloc[-2])
            if len(close) == 1:
                return float(close.iloc[0])
            return None
        except Exception as e:
            logger.error(f"Prev close fetch failed for {ticker}: {e}")
            return None

    def get_snapshots(self, tickers: List[str]) -> Dict[str, Any]:
        key = ",".join(sorted([t.upper() for t in tickers]))
        if key in self.cache:
            return self.cache[key]

        snapshots = []
        for raw in tickers:
            t = raw.upper()
            price = self._latest_price_1m(t)
            prev = self._prev_close(t)
            change = (price - prev) if (price is not None and prev is not None) else None
            change_percent = ((change / prev) * 100.0) if (change is not None and prev not in (None, 0)) else None
            snapshots.append({
                "ticker": t,
                "price": round(price, 2) if isinstance(price, (int, float)) else None,
                "prev_close": round(prev, 2) if isinstance(prev, (int, float)) else None,
                "change": round(change, 2) if isinstance(change, (int, float)) else None,
                "change_percent": round(change_percent, 2) if isinstance(change_percent, (int, float)) else None,
            })

        result = {"snapshots": snapshots}
        self.cache[key] = result
        return result


