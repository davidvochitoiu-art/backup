from app.data.db import get_connection

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    conn.close()
    return True

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result  # returns tuple (username, password) or None

def verify_user(username, password):
    user = get_user(username)
    if user is None:
        return False
    stored_user, stored_password = user
    return stored_password == password
