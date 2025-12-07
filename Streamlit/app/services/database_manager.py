import sqlite3
from typing import Any, Iterable

class DatabaseManager:
    """Handles SQLite connections and queries."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection = None

    def connect(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        self.connect()
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        self._connection.commit()
        return cursor

    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        self.connect()
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        self.connect()
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
