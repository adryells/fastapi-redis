from venv import logger

import websockets
import asyncio

async def subscribe():
    uri = "ws://localhost:8000/ws/stream"
    async with websockets.connect(uri) as websocket:
        while True:
            event = await websocket.recv()
            logger.info(f"Received event: {event}")


if __name__ == "__main__":
    asyncio.run(subscribe())
