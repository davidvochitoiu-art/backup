import sqlite3
import os

DB_PATH = os.path.join("DATA", "intelligence_platform.db")


def get_connection():
    """
    Returns a connection to the SQLite database.
    The DB file will be created automatically if it doesn't exist.
    """
    return sqlite3.connect(DB_PATH)
