import sqlite3
import bcrypt
from app.data.db import get_connection


# ------------------------------
# Password hashing helpers
# ------------------------------

def hash_password(plain_text_password: str) -> str:
    """Return a bcrypt hash for the given plain‐text password."""
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")  # store as TEXT in SQLite


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """Check a plain password against a stored bcrypt hash."""
    password_bytes = plain_text_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ------------------------------
# User CRUD / auth helpers
# ------------------------------

def create_user(username: str, password: str) -> bool:
    """
    Create a new user with a hashed password.

    Returns True if created, False if the username already exists
    or another DB error occurs.
    """
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # UNIQUE(username) violation → user already exists
        return False
    finally:
        conn.close()


def get_user(username: str):
    """
    Fetch a single user row.

    Returns (username, password_hash, role) or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password_hash, role FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def verify_user(username: str, password: str) -> bool:
    """
    Check login credentials.

    Returns True if username exists and password matches,
    otherwise False.
    """
    user = get_user(username)
    if user is None:
        return False

    stored_username, stored_hash, role = user
    return verify_password(password, stored_hash)
