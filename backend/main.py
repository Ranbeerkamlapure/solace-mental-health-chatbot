import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from core.config import CORS_ORIGINS
from core.deps import get_current_user
from database import ensure_indexes
from routes.auth import router as auth_router
from services.chat_service import get_chat_reply

logger = logging.getLogger("solace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

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
    logger.error("Database error on %s %s: %s", request.method, request.url.path, type(exc).__name__)
    return JSONResponse(
        status_code=503, content={"detail": "Service temporarily unavailable"}
    )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)  # 422 if empty or too long


@app.get("/")
def home():
    return {"message": "MindCare AI backend is running"}


@app.post("/chat")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    return {"response": get_chat_reply(request.message)}
