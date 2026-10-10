import sys

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from core.config import MONGODB_DB_NAME, MONGODB_URI  # raises a clear error if unset

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tz_aware=True)
db = client[MONGODB_DB_NAME]

# Collections
users_collection = db["users"]


def ensure_indexes() -> None:
    """Create required indexes. Safe to call on every startup."""
    try:
        users_collection.create_index(
            [("email", ASCENDING)], unique=True, name="uniq_email"
        )
    except PyMongoError as exc:
        raise RuntimeError(
            "Could not create the unique index on users.email "
            f"({type(exc).__name__}). Check that MongoDB is reachable and that "
            "no existing users share the same email."
        ) from None

def test_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print("Database connection error:", type(e).__name__)
        return False


if __name__ == "__main__":
    if test_connection():
        print("MongoDB connection successful!")
    else:
        print("MongoDB connection failed!")
        sys.exit(1)
