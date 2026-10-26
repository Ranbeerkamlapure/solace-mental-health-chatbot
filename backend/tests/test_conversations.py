"""Saved chats stay tied to the user who created them."""
import os
import unittest
from unittest import mock

from bson import ObjectId

os.environ.setdefault("MONGODB_URI", "mongodb://user:secret-pw@example.invalid:27017/")
os.environ.setdefault("JWT_SECRET", "x" * 40)
os.environ.setdefault("GROQ_API_KEY", "test-groq-key-not-real")

from services.conversation_service import (  # noqa: E402
    ConversationNotFound,
    add_message,
    delete_conversation,
    start_conversation,
)


class FakeCollection:
    def __init__(self):
        self.docs = []

    def insert_one(self, doc):
        doc["_id"] = ObjectId()
        self.docs.append(doc)
        return mock.Mock(inserted_id=doc["_id"])

    def find_one(self, query):
        for doc in self.docs:
            if doc["_id"] == query["_id"] and doc["user_id"] == query["user_id"]:
                return doc
        return None

    def update_one(self, query, update):
        for doc in self.docs:
            if doc["_id"] == query["_id"] and doc["user_id"] == query["user_id"]:
                doc["messages"] = [*doc.get("messages", []), *update["$push"]["messages"]["$each"]]
                doc["updated_at"] = update["$set"]["updated_at"]

    def delete_one(self, query):
        self.docs = [
            doc
            for doc in self.docs
            if not (doc["_id"] == query["_id"] and doc["user_id"] == query["user_id"])
        ]


class ConversationTests(unittest.TestCase):
    def test_a_chat_is_saved_and_hidden_from_another_user(self):
        collection = FakeCollection()
        owner = ObjectId()
        other = ObjectId()
        with (
            mock.patch("services.conversation_service.conversations_collection", collection),
            mock.patch("services.conversation_service.get_chat_reply", return_value="I am here."),
        ):
            saved = start_conversation(owner, "I feel lonely today")
            self.assertEqual(saved["messages"][0]["content"], "I feel lonely today")
            self.assertEqual(saved["messages"][1]["role"], "ai")
            with self.assertRaises(ConversationNotFound):
                add_message(other, saved["id"], "hello")
            delete_conversation(owner, saved["id"])
            with self.assertRaises(ConversationNotFound):
                delete_conversation(owner, saved["id"])


if __name__ == "__main__":
    unittest.main()
