"""
Para Adryell do futuro: Se o cookie manager do postman nao funcionar basta colocar a chave "Cookie" no header com o valor da sessão, ex.: session_id=194d6e35-99a7-4086-bcbc-adafba44e125
"""

import uvicorn
from fastapi import FastAPI, Request, Response
from uuid import uuid4
import json
import redis

app = FastAPI()

redis_client = redis.Redis(decode_responses=True)

SESSION_COOKIE = "session_id"
SESSION_EXPIRATION = 3600

def get_session_data(session_id: str):
    session_data = redis_client.get(session_id)
    return json.loads(session_data) if session_data else {}

def set_session_data(session_id: str, session_data: dict):
    redis_client.set(session_id, json.dumps(session_data), ex=SESSION_EXPIRATION)

async def get_session(request: Request, response: Response):
    session_id = request.cookies.get(SESSION_COOKIE)

    if session_id and redis_client.exists(session_id):
        session_data = get_session_data(session_id)
    else:
        session_id = str(uuid4())
        session_data = {}
        set_session_data(session_id, session_data)
        response.set_cookie(
            SESSION_COOKIE,
            session_id,
            max_age=SESSION_EXPIRATION,
            httponly=True,
            samesite="Strict",
            secure=False, # deve ser True em algum app em produção
        )

    return session_data, session_id


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    response = Response("Session Middleware")

    session_data, session_id = await get_session(request, response)

    request.state.session = session_data
    request.state.session_id = session_id

    response = await call_next(request)
    set_session_data(session_id, request.state.session)

    return response


@app.get("/login")
async def login(request: Request):
    request.state.session["user"] = "adryells"
    return {"message": "You're logged!"}

@app.get("/me")
async def me(request: Request):
    user = request.state.session.get("user")
    if not user:
        return {"message": "User unauthenticated."}
    return {"user": user}

@app.get("/logout")
async def logout(request: Request):
    request.state.session.clear()
    return {"message": "Closed session!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
