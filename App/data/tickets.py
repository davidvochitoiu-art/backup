from app.data.db import get_connection

def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM it_tickets")
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_ticket(ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours))
    conn.commit()
    conn.close()


def update_ticket_status(ticket_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE it_tickets
        SET status = ?
        WHERE ticket_id = ?
    """, (new_status, ticket_id))
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
