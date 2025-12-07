from app.models.User import User           # ✅ use app. and capital U
from app.services.database_manager import DatabaseManager
import bcrypt


class AuthManager:
    """Manages login, registration, and password hashing."""

    def __init__(self, db: DatabaseManager):
        self._db = db

    # -----------------------------
    # Password helpers (bcrypt)
    # -----------------------------
    def hash_password(self, plain: str) -> str:
        """Return a bcrypt hash for the given plain‐text password."""
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, plain: str, hashed: str) -> bool:
        """Check a plain password against a stored bcrypt hash."""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    # -----------------------------
    # Registration
    # -----------------------------
    def register_user(self, username: str, password: str, role: str = "user") -> None:
        """
        Create a new user in the database.

        Uses bcrypt hashing and stores into the existing Week 8 `users` table:
        (username, password_hash, role)
        """
        password_hash = self.hash_password(password)
        self._db.execute_query(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role),
        )

    # -----------------------------
    # Login
    # -----------------------------
    def login_user(self, username: str, password: str) -> User | None:
        """
        Validate credentials.

        Returns a User object on success, or None if login fails.
        """
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if not row:
            return None

        username_db, password_hash_db, role_db = row

        if self.check_password(password, password_hash_db):
            # Wrap DB row into your OOP User entity
            return User(username_db, password_hash_db, role_db)

        return None
