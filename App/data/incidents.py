from app.data.db import get_connection

def get_all_incidents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cyber_incidents')
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_incident(incident_id, timestamp, severity, category, status, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (incident_id, timestamp, severity, category, status, description))
    conn.commit()
    conn.close()

def update_incident_status(incident_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE cyber_incidents SET status = ? WHERE incident_id = ?', (new_status, incident_id))
    conn.commit()
    conn.close()

def delete_incident(incident_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cyber_incidents WHERE incident_id = ?', (incident_id,))
    conn.commit()
    conn.close()
