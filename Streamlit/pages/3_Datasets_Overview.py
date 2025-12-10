import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.dataset import Dataset

st.set_page_config(page_title="Datasets", layout="wide")

# ---------- LOGIN CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("📂 Dataset Metadata Overview")

# ---------- LOAD DATA ----------
db = DatabaseManager("DATA/intelligence_platform.db")

rows = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)

datasets = []
for row in rows:
    d = Dataset(
        dataset_id=row[0],
        name=row[1],
        rows=row[2],
        columns=row[3],
        uploaded_by=row[4],
        upload_date=row[5],
    )
    datasets.append(d)

records = []
for d in datasets:
    records.append(
        {
            "ID": d.get_id(),
            "Name": d.get_name(),
            "Rows": d.get_rows(),
            "Columns": d.get_columns(),
            "Uploaded By": d.get_uploaded_by(),
            "Upload Date": d.get_upload_date(),
            "Estimated Size (MB)": d.calculate_size_mb(),
        }
    )

df = pd.DataFrame(records)

# ---------- TABLE ----------
st.subheader("Dataset Records")
st.dataframe(df, use_container_width=True)

# ---------- CHARTS ----------
if not df.empty:
    st.subheader("🌞 Dataset Structure (Sunburst)")

    sunburst_df = df.copy()
    sunburst_df["Size_MB"] = sunburst_df["Estimated Size (MB)"]

    fig_sunburst = px.sunburst(
        sunburst_df,
        path=["Uploaded By", "Name"],
        values="Size_MB",
        title="Dataset Size by Uploader and Dataset",
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.subheader("📈 Size Distribution (MB)")
    st.bar_chart(df["Estimated Size (MB)"])

    st.subheader("📊 Rows per Dataset")
    if "Name" in df.columns:
        line_data = df.set_index("Name")["Rows"]
        st.line_chart(line_data)
else:
    st.info("No datasets yet. Add one below.")

# ---------- CRUD ----------
st.markdown("---")
st.header("✏️ Manage Datasets (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create", "📝 Update", "🗑️ Delete"]
)

# CREATE
with tab_create:
    st.subheader("Create a New Dataset")

    c1, c2 = st.columns(2)

    with c1:
        new_id = st.number_input(
            "Dataset ID",
            min_value=1,
            step=1,
            key="dataset_create_id",
        )
        new_name = st.text_input(
            "Dataset Name",
            key="dataset_create_name",
        )
        new_rows = st.number_input(
            "Rows",
            min_value=0,
            step=1,
            key="dataset_create_rows",
        )
        new_cols = st.number_input(
            "Columns",
            min_value=0,
            step=1,
            key="dataset_create_cols",
        )

    with c2:
        new_uploader = st.text_input(
            "Uploaded By",
            key="dataset_create_uploader",
        )
        default_date = datetime.now().strftime("%Y-%m-%d")
        new_date = st.text_input(
            "Upload Date",
            value=default_date,
            key="dataset_create_date",
        )

    if st.button("Create Dataset", key="dataset_create_button"):
        if not new_name or not new_uploader:
            st.warning("Please fill in name and uploader.")
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
                        new_date,
                    ),
                )
                st.success(f"Dataset {int(new_id)} created.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating dataset: {e}")

# UPDATE
with tab_update:
    st.subheader("Update Dataset")

    if df.empty:
        st.info("No datasets to update.")
    else:
        id_list = df["ID"].tolist()
        selected_id = st.selectbox(
            "Select Dataset ID",
            id_list,
            key="dataset_update_id",
        )

        current = df[df["ID"] == selected_id].iloc[0]

        u1, u2 = st.columns(2)

        with u1:
            upd_name = st.text_input(
                "Name",
                value=current["Name"],
                key="dataset_update_name",
            )
            upd_rows = st.number_input(
                "Rows",
                min_value=0,
                step=1,
                value=int(current["Rows"]),
                key="dataset_update_rows",
            )
            upd_cols = st.number_input(
                "Columns",
                min_value=0,
                step=1,
                value=int(current["Columns"]),
                key="dataset_update_cols",
            )

        with u2:
            upd_uploader = st.text_input(
                "Uploaded By",
                value=current["Uploaded By"],
                key="dataset_update_uploader",
            )
            upd_date = st.text_input(
                "Upload Date",
                value=current["Upload Date"],
                key="dataset_update_date",
            )

        if st.button("Update Dataset", key="dataset_update_button"):
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
                        int(selected_id),
                    ),
                )
                st.success(f"Dataset {int(selected_id)} updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating dataset: {e}")

# DELETE
with tab_delete:
    st.subheader("Delete Dataset")

    if df.empty:
        st.info("No datasets to delete.")
    else:
        id_list = df["ID"].tolist()
        delete_id = st.selectbox(
            "Select Dataset ID to delete",
            id_list,
            key="dataset_delete_id",
        )

        confirm = st.checkbox(
            "I confirm I want to permanently delete this dataset.",
            key="dataset_delete_confirm",
        )

        if st.button(
            "Delete Dataset",
            type="primary",
            disabled=not confirm,
            key="dataset_delete_button",
        ):
            try:
                db.execute_query(
                    "DELETE FROM datasets_metadata WHERE dataset_id = ?",
                    (int(delete_id),),
                )
                st.success(f"Dataset {int(delete_id)} deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting dataset: {e}")
