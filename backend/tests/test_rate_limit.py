"""Chat sends are limited per user, without calling Groq or MongoDB."""
import os
import unittest

os.environ.setdefault("MONGODB_URI", "mongodb://user:secret-pw@example.invalid:27017/")
os.environ.setdefault("JWT_SECRET", "x" * 40)

from core.rate_limit import (  # noqa: E402
    DAILY_LIMIT,
    RateLimitError,
    check_chat_rate_limit,
    reset_rate_limits,
)


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        reset_rate_limits()

    def test_a_second_immediate_send_is_rejected(self):
        check_chat_rate_limit("user-1")
        with self.assertRaises(RateLimitError):
            check_chat_rate_limit("user-1")

    def test_another_user_is_not_blocked(self):
        check_chat_rate_limit("user-1")
        check_chat_rate_limit("user-2")

    def test_daily_cap_is_enforced(self):
        with unittest.mock.patch("core.rate_limit.time.monotonic", return_value=0):
            for _ in range(DAILY_LIMIT):
                check_chat_rate_limit("user-1")
                # Move the clock forward so the short interval does not trip first.
                # The patch is a constant, so reset the last-sent time instead.
                from core import rate_limit

                rate_limit._last_sent["user-1"] = -10
            with self.assertRaises(RateLimitError) as ctx:
                check_chat_rate_limit("user-1")
        self.assertIn("today", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
