# app/data/load_csv.py
import os
import pandas as pd
from app.data.db import get_connection


def _load_csv_to_table(csv_path, table_name):
    if not os.path.exists(csv_path):
        print(f"WARNING: {csv_path} not found, skipping.")
        return

    conn = get_connection()
    df = pd.read_csv(csv_path)

    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()
    print(f"✓ Loaded {len(df)} rows into {table_name}")


def load_all_csv():
    _load_csv_to_table("DATA/cyber_incidents.csv", "cyber_incidents")
    _load_csv_to_table("DATA/datasets_metadata.csv", "datasets_metadata")
    _load_csv_to_table("DATA/it_tickets.csv", "it_tickets")
