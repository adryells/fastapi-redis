from venv import logger

import websockets
import asyncio

async def subscribe():
    uri = "ws://localhost:8000/ws/news"
    async with websockets.connect(uri) as websocket:
        logger.info("Subscribed to channel: news")
        while True:
            message = await websocket.recv()
            logger.info(f"Received message: {message}")


if __name__ == "__main__":
    asyncio.run(subscribe())
