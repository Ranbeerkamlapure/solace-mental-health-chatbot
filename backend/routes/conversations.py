from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user
from core.rate_limit import RateLimitError, check_chat_rate_limit
from schemas.chat import ConversationPublic, MessageIn
from services.conversation_service import (
    ConversationNotFound,
    add_message,
    delete_conversation,
    list_conversations,
    start_conversation,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _limit(user: dict) -> None:
    try:
        check_chat_rate_limit(str(user["_id"]))
    except RateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=exc.detail) from None


@router.get("", response_model=list[ConversationPublic])
def list_mine(current_user: dict = Depends(get_current_user)):
    return list_conversations(current_user["_id"])


@router.post("", response_model=ConversationPublic, status_code=status.HTTP_201_CREATED)
def create(body: MessageIn, current_user: dict = Depends(get_current_user)):
    _limit(current_user)
    return start_conversation(current_user["_id"], body.message)


@router.post("/{conversation_id}/messages", response_model=ConversationPublic)
def send(conversation_id: str, body: MessageIn, current_user: dict = Depends(get_current_user)):
    _limit(current_user)
    try:
        return add_message(current_user["_id"], conversation_id, body.message)
    except ConversationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(conversation_id: str, current_user: dict = Depends(get_current_user)):
    try:
        delete_conversation(current_user["_id"], conversation_id)
    except ConversationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
