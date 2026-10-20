"""Saved chats. Every query is limited to the signed-in user."""
from bson import ObjectId
from bson.errors import InvalidId

from database import conversations_collection
from models.user import utcnow
from services.chat_service import get_chat_reply


class ConversationNotFound(Exception):
    """No conversation with this id belongs to this user."""


def _title(message: str) -> str:
    text = " ".join(message.split())
    if len(text) <= 40:
        return text
    return text[:40] + "…"


def _public_message(message: dict) -> dict:
    role = "ai" if message["role"] == "assistant" else "user"
    return {"role": role, "content": message["content"]}


def _public(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "messages": [_public_message(message) for message in doc.get("messages", [])],
        "updated_at": doc["updated_at"],
    }


def list_conversations(user_id: ObjectId) -> list[dict]:
    cursor = conversations_collection.find({"user_id": user_id}).sort("updated_at", -1)
    return [_public(doc) for doc in cursor]


def _owned(user_id: ObjectId, conversation_id: str) -> dict:
    try:
        oid = ObjectId(conversation_id)
    except InvalidId:
        raise ConversationNotFound from None
    doc = conversations_collection.find_one({"_id": oid, "user_id": user_id})
    if doc is None:
        raise ConversationNotFound
    return doc


def delete_conversation(user_id: ObjectId, conversation_id: str) -> None:
    doc = _owned(user_id, conversation_id)
    conversations_collection.delete_one({"_id": doc["_id"], "user_id": user_id})


def _store_exchange(doc: dict, message: str) -> dict:
    prior = [
        {"role": item["role"], "content": item["content"]}
        for item in doc.get("messages", [])
        if item.get("role") in ("user", "assistant")
    ][-8:]
    reply = get_chat_reply(message, prior)
    now = utcnow()
    stored = [
        {"role": "user", "content": message, "created_at": now},
        {"role": "assistant", "content": reply, "created_at": now},
    ]
    conversations_collection.update_one(
        {"_id": doc["_id"], "user_id": doc["user_id"]},
        {"$push": {"messages": {"$each": stored}}, "$set": {"updated_at": now}},
    )
    doc["messages"] = [*doc.get("messages", []), *stored]
    doc["updated_at"] = now
    return doc


def start_conversation(user_id: ObjectId, message: str) -> dict:
    now = utcnow()
    doc = {
        "user_id": user_id,
        "title": _title(message),
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }
    doc["_id"] = conversations_collection.insert_one(doc).inserted_id
    return _public(_store_exchange(doc, message))


def add_message(user_id: ObjectId, conversation_id: str, message: str) -> dict:
    doc = _owned(user_id, conversation_id)
    return _public(_store_exchange(doc, message))
