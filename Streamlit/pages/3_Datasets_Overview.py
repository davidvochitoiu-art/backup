import streamlit as st
import pandas as pd
from app.services.database_manager import DatabaseManager
from app.models.dataset import Dataset

st.set_page_config(page_title="Datasets Overview", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("📂 Dataset Metadata Analytics")

db = DatabaseManager("DATA/intelligence_platform.db")

rows = db.fetch_all("""
    SELECT dataset_id, name, rows, columns, uploaded_by, upload_date
    FROM datasets_metadata
""")

datasets = [Dataset(*row) for row in rows]

df = pd.DataFrame([{
    "ID": d.get_id(),
    "Name": d.get_name(),
    "Rows": d.get_rows(),
    "Columns": d.get_columns(),
    "Uploaded By": d.get_uploaded_by(),
    "Upload Date": d.get_upload_date(),
    "Estimated Size (MB)": d.calculate_size_mb()
} for d in datasets])

st.subheader("Dataset Records")
st.dataframe(df, use_container_width=True)

# =============== CHARTS ===============
st.subheader("Dataset Size Distribution")
st.bar_chart(df["Estimated Size (MB)"])

st.subheader("Rows per Dataset")
st.line_chart(df["Rows"])
