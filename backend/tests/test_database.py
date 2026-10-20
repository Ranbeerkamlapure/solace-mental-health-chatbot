"""Run from the backend folder:  python -m unittest discover tests -v
No real database is needed: the MongoClient is lazy and the collection is faked."""
import os
import unittest
from unittest import mock

os.environ.setdefault("MONGODB_URI", "mongodb://user:secret-pw@example.invalid:27017/")
os.environ.setdefault("JWT_SECRET", "x" * 40)

import database  # noqa: E402
from pymongo.errors import PyMongoError  # noqa: E402


class DatabaseErrorTests(unittest.TestCase):
    def test_tls_error_gets_a_hint_and_never_leaks_the_uri(self):
        err = PyMongoError(f"SSL handshake failed: [SSL: TLSV1_ALERT_INTERNAL_ERROR] {database.MONGODB_URI}")
        text = database.describe_db_error(err)
        self.assertIn("IP Access List", text)
        self.assertNotIn("secret-pw", text)

    def test_startup_fails_loudly_when_database_is_unreachable(self):
        fake = mock.Mock()
        fake.create_index.side_effect = PyMongoError("SSL handshake failed: TLSV1_ALERT_INTERNAL_ERROR")
        with mock.patch.object(database, "users_collection", fake):
            with self.assertRaises(RuntimeError) as ctx:
                database.ensure_indexes()
        self.assertIn("Network Access", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, PyMongoError)  # original error kept

    def test_startup_ok_when_index_is_created(self):
        users = mock.Mock()
        conversations = mock.Mock()
        with (
            mock.patch.object(database, "users_collection", users),
            mock.patch.object(database, "conversations_collection", conversations),
        ):
            database.ensure_indexes()
        users.create_index.assert_called_once()
        self.assertTrue(users.create_index.call_args.kwargs["unique"])
        conversations.create_index.assert_called_once()


if __name__ == "__main__":
    unittest.main()
