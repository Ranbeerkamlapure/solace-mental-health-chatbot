import sys

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from core.config import MONGODB_DB_NAME, MONGODB_URI  # raises a clear error if unset

# PyMongo's default. A 5s cap expires before a cold Atlas handshake finishes,
# and the driver then falls through to another address whose TLS handshake can fail.
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=30000, tz_aware=True)
db = client[MONGODB_DB_NAME]

# Collections
users_collection = db["users"]
conversations_collection = db["conversations"]


def describe_db_error(exc: Exception) -> str:
    """Short, safe description of a database error (never includes the URI or password)."""
    text = " ".join(str(exc).split())[:400]
    if MONGODB_URI and MONGODB_URI in text:
        text = text.replace(MONGODB_URI, "<MONGODB_URI>")
    message = f"{type(exc).__name__}: {text}"
    if "SSL handshake failed" in text or "TLSV1_ALERT" in text:
        message += (
            "\nHint: Atlas refused the TLS handshake. The usual cause is that this "
            "computer's IP address is not in Atlas > Network Access > IP Access List "
            "(or the cluster is paused). A VPN or antivirus that inspects HTTPS can also "
            "cause it. TLS verification is NOT disabled and should stay that way."
        )
    return message


def ensure_indexes() -> None:
    """Create required indexes. Safe to call on every startup.

    If MongoDB is unreachable the app refuses to start (with a clear message)
    instead of pretending the database is ready.
    """
    try:
        users_collection.create_index(
            [("email", ASCENDING)], unique=True, name="uniq_email"
        )
        conversations_collection.create_index(
            [("user_id", ASCENDING), ("updated_at", DESCENDING)],
            name="user_updated",
        )
    except PyMongoError as exc:
        raise RuntimeError(
            "Could not create the unique index on users.email. "
            "Check that MongoDB Atlas is reachable and that no existing users share "
            f"the same email.\n{describe_db_error(exc)}"
        ) from exc


def test_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print("Database connection error:", describe_db_error(e))
        return False


if __name__ == "__main__":
    if test_connection():
        print("MongoDB connection successful!")
    else:
        print("MongoDB connection failed!")
        sys.exit(1)
