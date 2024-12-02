from venv import logger

import uvicorn
from fastapi import FastAPI, WebSocket
from redis.asyncio import Redis

app = FastAPI()

redis_client = Redis(host="localhost", port=6379, decode_responses=True)


@app.post("/publish/{channel}")
async def publish(channel: str, message: str):
    await redis_client.publish(channel, message)
    return {"status": "Message sent", "channel": channel, "message": message}


@app.websocket("/ws/{channel}")
async def websocket_subscriber(websocket: WebSocket, channel: str):
    await websocket.accept()

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except Exception as exception:
        logger.error(f"Error: {exception}")
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


if __name__ == "__main__":
    uvicorn.run(app)