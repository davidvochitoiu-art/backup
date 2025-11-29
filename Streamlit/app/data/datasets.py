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


# ---------------------------------------------------------
# ✅ NEW FUNCTION (for Dataset Line Chart in Streamlit)
# ---------------------------------------------------------
def get_dataset_growth():
    """
    Returns dates + total rows uploaded per day.
    Useful for line-chart visualization in Streamlit.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT upload_date, SUM(rows)
        FROM datasets_metadata
        GROUP BY upload_date
        ORDER BY upload_date
    """)
    results = cursor.fetchall()
    conn.close()
    return results
