from app.data.db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id INTEGER PRIMARY KEY,
            timestamp TEXT,
            severity TEXT,
            category TEXT,
            status TEXT,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rows INTEGER,
            columns INTEGER,
            uploaded_by TEXT,
            upload_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            priority TEXT,
            description TEXT,
            status TEXT,
            assigned_to TEXT,
            created_at TEXT,
            resolution_time_hours INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print('✓ Tables created / verified successfully.')
