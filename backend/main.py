import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from core.config import CORS_ORIGINS
from core.deps import get_current_user
from core.rate_limit import RateLimitError, check_chat_rate_limit
from database import describe_db_error, ensure_indexes
from routes.auth import router as auth_router
from routes.conversations import router as conversations_router
from services.chat_service import get_chat_reply

logger = logging.getLogger("solace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(conversations_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PyMongoError)
async def database_error_handler(request: Request, exc: PyMongoError):
    # Log details server-side; never expose database internals to the client.
    logger.error("Database error on %s %s: %s", request.method, request.url.path, describe_db_error(exc))
    return JSONResponse(
        status_code=503, content={"detail": "Service temporarily unavailable"}
    )


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)  # 422 if empty or too long
    history: list[HistoryTurn] = Field(default_factory=list, max_length=8)


@app.get("/")
def home():
    return {"message": "MindCare AI backend is running"}


@app.post("/chat")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        check_chat_rate_limit(str(current_user["_id"]))
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail=exc.detail) from None
    history = [turn.model_dump() for turn in request.history]
    return {"response": get_chat_reply(request.message, history)}
