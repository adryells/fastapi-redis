from venv import logger

import uvicorn
from fastapi import FastAPI, WebSocket
from redis.asyncio import Redis
from uuid import uuid4

app = FastAPI()

redis_client = Redis(decode_responses=True)

STREAM_NAME = "real_time_analysis"
CONSUMER_GROUP = "analytics_group"
CONSUMER_NAME = f"consumer_{uuid4()}"


@app.on_event("startup")
async def setup():
    try:
        await redis_client.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
    except Exception as exception:
        logger.error(f"Error: {exception}")


@app.post("/produce/")
async def produce_event(event: dict):
    event_id = await redis_client.xadd(STREAM_NAME, event)
    return {"status": "Event added", "event_id": event_id, "event": event}


@app.websocket("/ws/stream")
async def websocket_consumer(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            events = await redis_client.xreadgroup(
                groupname=CONSUMER_GROUP,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=10,
                block=5000,
            )

            for stream, messages in events:
                for message_id, message in messages:
                    await websocket.send_json({"id": message_id, "data": message})

                    await redis_client.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
    except Exception as exception:
        logger.error(f"WS Error: {exception}")
    finally:
        await websocket.close()


@app.get("/stats/")
async def get_stream_stats():
    info = await redis_client.xinfo_stream(STREAM_NAME)
    return {"stream_info": info}


if __name__ == "__main__":
    uvicorn.run(app)
