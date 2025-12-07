import streamlit as st
import pandas as pd
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.dataset import Dataset

st.set_page_config(page_title="Datasets Overview", layout="wide")

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("📂 Dataset Metadata Analytics")

db = DatabaseManager("DATA/intelligence_platform.db")

# Load datasets
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


# ================= TABLE =================
st.subheader("Dataset Records")
st.dataframe(df, use_container_width=True)

# ================= CHARTS =================
if not df.empty:
    st.subheader("Dataset Size Distribution")
    st.bar_chart(df["Estimated Size (MB)"])

    st.subheader("Rows per Dataset")
    st.line_chart(df["Rows"])
else:
    st.info("No datasets found in the system yet.")


# =========================================================
#                CRUD SECTION (Create / Update / Delete)
# =========================================================
st.markdown("---")
st.header("✏️ Manage Datasets (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create Dataset", "📝 Update Dataset", "🗑️ Delete Dataset"]
)


# --------------------------------------------------------
#                     CREATE DATASET
# --------------------------------------------------------
with tab_create:
    st.subheader("Create New Dataset")

    col1, col2 = st.columns(2)

    with col1:
        new_id = st.number_input("Dataset ID", min_value=1, step=1)
        new_name = st.text_input("Dataset Name")
        new_rows = st.number_input("Rows", min_value=0, step=1)
        new_cols = st.number_input("Columns", min_value=0, step=1)

    with col2:
        new_uploader = st.text_input("Uploaded By")
        default_date = datetime.now().strftime("%Y-%m-%d")
        new_date = st.text_input("Upload Date", value=default_date)

    if st.button("Create Dataset"):
        if not new_name or not new_uploader:
            st.warning("Please fill in the dataset name and uploader.")
        else:
            try:
                db.execute_query(
                    """
                    INSERT INTO datasets_metadata
                        (dataset_id, name, rows, columns, uploaded_by, upload_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(new_id),
                        new_name,
                        int(new_rows),
                        int(new_cols),
                        new_uploader,
                        new_date
                    ),
                )
                st.success(f"Dataset {int(new_id)} created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating dataset: {e}")


# --------------------------------------------------------
#                     UPDATE DATASET
# --------------------------------------------------------
with tab_update:
    st.subheader("Update Dataset Metadata")

    if df.empty:
        st.info("No datasets available to update.")
    else:
        dataset_ids = df["ID"].tolist()
        selected_id = st.selectbox("Select Dataset ID", dataset_ids)

        selected_row = df[df["ID"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            upd_name = st.text_input("Name", value=selected_row["Name"])
            upd_rows = st.number_input("Rows", min_value=0, step=1, value=int(selected_row["Rows"]))
            upd_cols = st.number_input("Columns", min_value=0, step=1, value=int(selected_row["Columns"]))

        with col2:
            upd_uploader = st.text_input("Uploaded By", value=selected_row["Uploaded By"])
            upd_date = st.text_input("Upload Date", value=selected_row["Upload Date"])

        if st.button("Update Dataset"):
            try:
                db.execute_query(
                    """
                    UPDATE datasets_metadata
                    SET name = ?, rows = ?, columns = ?, uploaded_by = ?, upload_date = ?
                    WHERE dataset_id = ?
                    """,
                    (
                        upd_name,
                        int(upd_rows),
                        int(upd_cols),
                        upd_uploader,
                        upd_date,
                        int(selected_id)
                    ),
                )
                st.success(f"Dataset {selected_id} updated successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating dataset: {e}")


# --------------------------------------------------------
#                     DELETE DATASET
# --------------------------------------------------------
with tab_delete:
    st.subheader("Delete Dataset")

    if df.empty:
        st.info("No datasets available to delete.")
    else:
        dataset_ids = df["ID"].tolist()
        delete_id = st.selectbox("Select Dataset ID to Delete", dataset_ids)

        confirm = st.checkbox(
            "I understand this will permanently delete the dataset.",
            value=False
        )

        if st.button("Delete Dataset", type="primary", disabled=not confirm):
            try:
                db.execute_query(
                    "DELETE FROM datasets_metadata WHERE dataset_id = ?",
                    (int(delete_id),)
                )
                st.success(f"Dataset {int(delete_id)} deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting dataset: {e}")
