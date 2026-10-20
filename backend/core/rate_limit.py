"""In-memory limits for chat sends. One process, reset when the server restarts."""
import time

MIN_INTERVAL_SECONDS = 2
DAILY_LIMIT = 100

_last_sent: dict[str, float] = {}
_daily_count: dict[str, tuple[str, int]] = {}


class RateLimitError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


def reset_rate_limits() -> None:
    _last_sent.clear()
    _daily_count.clear()


def check_chat_rate_limit(user_id: str) -> None:
    """Raise RateLimitError when this user is sending too fast or too often today."""
    now = time.monotonic()
    previous = _last_sent.get(user_id)
    if previous is not None and now - previous < MIN_INTERVAL_SECONDS:
        raise RateLimitError("Please wait a moment before sending another message.")

    today = time.strftime("%Y-%m-%d", time.gmtime())
    stored_day, count = _daily_count.get(user_id, (today, 0))
    if stored_day != today:
        count = 0
    if count >= DAILY_LIMIT:
        raise RateLimitError("You've reached today's message limit. It resets tomorrow.")

    _last_sent[user_id] = now
    _daily_count[user_id] = (today, count + 1)
