# app/data/incidents.py
from app.data.db import get_connection


def create_incident(title, severity, status="open", date=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cyber_incidents (title, severity, status, date)
        VALUES (?, ?, ?, ?)
    """, (title, severity, status, date))

    conn.commit()
    conn.close()


def get_all_incidents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, severity, status, date FROM cyber_incidents")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_incident_status(incident_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cyber_incidents
        SET status = ?
        WHERE id = ?
    """, (new_status, incident_id))

    conn.commit()
    conn.close()


def delete_incident(incident_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))

    conn.commit()
    conn.close()
