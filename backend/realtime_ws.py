from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
import logging
from realtime_prices import RealTimePriceService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def send_json(self, websocket: WebSocket, data):
        await websocket.send_text(json.dumps(data))


manager = ConnectionManager()


async def stream_prices(websocket: WebSocket, tickers: List[str], interval_seconds: int = 5):
    """Continuously stream near real-time snapshots for tickers over WebSocket."""
    svc = RealTimePriceService(ttl_seconds=max(1, interval_seconds - 1))
    try:
        while True:
            try:
                payload = svc.get_snapshots([t.upper() for t in tickers])
                await manager.send_json(websocket, payload)
            except Exception as e:
                logger.error(f"WS stream error: {e}")
                await manager.send_json(websocket, {"error": str(e)})
            await asyncio.sleep(interval_seconds)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS stream terminated: {e}")
        manager.disconnect(websocket)


