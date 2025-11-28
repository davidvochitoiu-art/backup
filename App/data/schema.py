# app/data/schema.py
from app.data.db import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------------------
    # USERS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    # ---------------------------
    # CYBER INCIDENTS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            date TEXT
        )
    """)

    # ---------------------------
    # DATASETS METADATA TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT,
            category TEXT,
            size INTEGER
        )
    """)

    # ---------------------------
    # IT TICKETS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_date TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✓ Tables created / verified successfully.")


if __name__ == "__main__":
    create_tables()
