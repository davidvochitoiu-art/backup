# app/data/tickets.py
from app.data.db import get_connection


def create_ticket(title, priority, status="open", created_date=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets (title, priority, status, created_date)
        VALUES (?, ?, ?, ?)
    """, (title, priority, status, created_date))

    conn.commit()
    conn.close()


def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, priority, status, created_date FROM it_tickets")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_ticket_status(ticket_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE it_tickets
        SET status = ?
        WHERE id = ?
    """, (new_status, ticket_id))

    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM it_tickets WHERE id = ?", (ticket_id,))

    conn.commit()
    conn.close()
