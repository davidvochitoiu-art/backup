# app/data/datasets.py
from app.data.db import get_connection


def create_dataset(name, source, category, size):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO datasets_metadata (name, source, category, size)
        VALUES (?, ?, ?, ?)
    """, (name, source, category, size))

    conn.commit()
    conn.close()


def get_all_datasets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, source, category, size FROM datasets_metadata")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_dataset_size(dataset_id, new_size):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE datasets_metadata
        SET size = ?
        WHERE id = ?
    """, (new_size, dataset_id))

    conn.commit()
    conn.close()


def delete_dataset(dataset_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))

    conn.commit()
    conn.close()
