"""Crisis replies stay fixed; ordinary replies use Groq or raise when it fails."""
import os
import unittest
from unittest import mock

os.environ.setdefault("MONGODB_URI", "mongodb://user:secret-pw@example.invalid:27017/")
os.environ.setdefault("JWT_SECRET", "x" * 40)
os.environ.setdefault("GROQ_API_KEY", "test-groq-key-not-real")

from services.chat_service import (  # noqa: E402
    CRISIS_RESPONSE,
    ChatServiceUnavailable,
    get_chat_reply,
)


class ChatServiceTests(unittest.TestCase):
    def test_crisis_phrase_is_not_sent_to_groq(self):
        with mock.patch("services.chat_service.groq_reply") as groq:
            reply = get_chat_reply("I want to die")
        self.assertEqual(reply, CRISIS_RESPONSE)
        groq.assert_not_called()

    def test_successful_groq_response_is_returned(self):
        with mock.patch(
            "services.chat_service.groq_reply",
            return_value="That sounds really hard. What feels heaviest right now?",
        ):
            reply = get_chat_reply("I feel lonely")
        self.assertEqual(
            reply, "That sounds really hard. What feels heaviest right now?"
        )

    def test_failed_groq_call_raises_service_unavailable(self):
        with mock.patch("services.chat_service.groq_reply", return_value=None):
            with self.assertRaises(ChatServiceUnavailable) as ctx:
                get_chat_reply("I feel lonely")
        self.assertIn("unavailable", ctx.exception.detail.lower())


if __name__ == "__main__":
    unittest.main()
