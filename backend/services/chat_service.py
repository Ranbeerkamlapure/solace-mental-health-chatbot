"""Chat replies. Crisis phrases always get a fixed answer. Other messages use Groq."""
import json
import logging
import re
import urllib.error
import urllib.request

from core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("solace")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = (
    "You are Solace, a calm, kind listener for students. "
    "You are not a therapist, doctor, or crisis service, and you never diagnose. "
    "Reply to the exact feeling in the latest message, in 2 to 4 short sentences, in plain language. "
    "Do not cheer a sad or self-critical message. "
    "Ask one gentle question when it fits. "
    "If the person may be in immediate danger or talking about suicide or self-harm, "
    "say you cannot help in a crisis and tell them to contact local emergency services "
    "(112 in India, 911 in the US) or Tele-MANAS at 14416."
)

# Crisis phrases are checked first. If any appear, we always return CRISIS_RESPONSE.
# Phrases are lowercase, without apostrophes. This list is not comprehensive.
CRISIS_PHRASES = [
    "kill myself", "killing myself", "end my life", "ending my life", "end my own life",
    "end it all", "ending it all", "take my own life", "taking my own life",
    "want to die", "wanna die", "want to be dead", "better off dead", "no reason to live",
    "hurt myself", "hurting myself", "harm myself", "harming myself",
    "cut myself", "cutting myself", "self harm",
    "dont want to live", "do not want to live", "dont want to be alive",
    "suicide", "suicidal",
]

CRISIS_RESPONSE = (
    "I'm really sorry you're going through this, and I'm glad you told me. "
    "You deserve support right now, and I'm not able to give you the help you need in a crisis.\n\n"
    "If you are in immediate danger or might act on these thoughts, please call your local "
    "emergency number now (112 in India, 911 in the US).\n\n"
    "You can also talk to a trained person at any time:\n"
    "- India: Tele-MANAS, 14416 or 1800-891-4416 (free, 24/7)\n"
    "- US: call or text 988\n"
    "- Elsewhere: findahelpline.com lists crisis lines by country\n\n"
    "Please also tell someone you trust, like a friend, family member or teacher, "
    "how you are feeling so you are not alone with this."
)

SERVICE_UNAVAILABLE_DETAIL = (
    "Chat replies are temporarily unavailable. Please try again in a moment."
)


class ChatServiceUnavailable(Exception):
    """Raised when Groq cannot produce a reply for a non-crisis message."""

    def __init__(self, detail: str = SERVICE_UNAVAILABLE_DETAIL):
        self.detail = detail
        super().__init__(detail)


def _normalize_for_match(message: str) -> str:
    """Lowercase, strip apostrophes, keep words with spaces for whole-phrase matching."""
    text = message.lower().replace("'", "").replace("’", "")
    words = re.findall(r"[a-z]+", text)
    return " " + " ".join(words) + " "


def _has_phrase(normalized: str, phrase: str) -> bool:
    return " " + phrase + " " in normalized


def _clean_reply(text):
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:2000]


def groq_reply(message, history):
    """Ask Groq for a reply. Returns None when the call fails."""
    if not GROQ_API_KEY:
        return None

    turns = []
    for turn in history[-8:]:
        role = turn.get("role")
        content = str(turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            turns.append({"role": role, "content": content[:1000]})
    if turns and turns[-1]["role"] == "user" and turns[-1]["content"] == message.strip():
        turns.pop()

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *turns, {"role": "user", "content": message.strip()[:1000]}],
        "temperature": 0.6,
        "max_tokens": 400,
    }
    # Cloudflare rejects urllib's default User-Agent with HTTP 403.
    request = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "solace-backend/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode())
        text = _clean_reply(data["choices"][0]["message"].get("content") or "")
        return text or None
    except urllib.error.HTTPError as exc:
        logger.warning("Groq reply failed: HTTP %s", exc.code)
        return None
    except Exception as exc:
        logger.warning("Groq reply failed: %s", type(exc).__name__)
        return None


def get_chat_reply(message, history=None):
    normalized = _normalize_for_match(message)

    # Crisis check stays fixed and is not sent to Groq.
    for phrase in CRISIS_PHRASES:
        if _has_phrase(normalized, phrase):
            return CRISIS_RESPONSE

    reply = groq_reply(message, history or [])
    if reply:
        return reply
    raise ChatServiceUnavailable()
