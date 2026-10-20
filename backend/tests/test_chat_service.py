"""Crisis replies stay fixed, and a failed model call falls back to a written reply."""
import os
import unittest
from unittest import mock

os.environ.setdefault("MONGODB_URI", "mongodb://user:secret-pw@example.invalid:27017/")
os.environ.setdefault("JWT_SECRET", "x" * 40)

from services.chat_service import CRISIS_RESPONSE, get_chat_reply  # noqa: E402


class ChatServiceTests(unittest.TestCase):
    def test_crisis_phrase_is_not_sent_to_groq(self):
        with mock.patch("services.chat_service.groq_reply") as groq:
            reply = get_chat_reply("I want to die")
        self.assertEqual(reply, CRISIS_RESPONSE)
        groq.assert_not_called()

    def test_failed_model_call_uses_the_written_reply(self):
        with mock.patch("services.chat_service.groq_reply", return_value=None):
            reply = get_chat_reply("I feel lonely")
        self.assertIn("lonely", reply.lower())


if __name__ == "__main__":
    unittest.main()
