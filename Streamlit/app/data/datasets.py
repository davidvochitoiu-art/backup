from app.data.db import get_connection

def get_all_datasets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM datasets_metadata')
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO datasets_metadata (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (dataset_id, name, rows, columns, uploaded_by, upload_date))
    conn.commit()
    conn.close()

def delete_dataset(dataset_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM datasets_metadata WHERE dataset_id = ?', (dataset_id,))
    conn.commit()
    conn.close()
