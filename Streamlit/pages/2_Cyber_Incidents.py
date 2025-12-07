import streamlit as st
import pandas as pd
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident

st.set_page_config(page_title="Cyber Incidents", layout="wide")

# ================= LOGIN CHECK =================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("🛡️ Cybersecurity Incidents Analysis")

# ================= DATABASE =================
db = DatabaseManager("DATA/intelligence_platform.db")

# Load incidents (no timestamp in this view)
rows = db.fetch_all(
    """
    SELECT incident_id, category, severity, status, description
    FROM cyber_incidents
    """
)

incidents = [
    SecurityIncident(
        incident_id=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4]
    )
    for row in rows
]

df = pd.DataFrame([{
    "ID": inc.get_id(),
    "Category": inc.get_incident_type(),
    "Severity": inc.get_severity(),
    "Status": inc.get_status(),
    "Description": inc.get_description(),
    "Severity Level (1–4)": inc.get_severity_level()
} for inc in incidents])

# Guard if no data
if df.empty:
    st.info("No incidents found in the database yet.")


# ================= FILTER SECTION =================
st.subheader("Filters")

if not df.empty:
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All"] + sorted(df["Severity"].dropna().unique().tolist())
    )
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + sorted(df["Status"].dropna().unique().tolist())
    )

    filtered_df = df.copy()

    if severity_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Severity"].str.lower() == severity_filter.lower()
        ]

    if status_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Status"].str.lower() == status_filter.lower()
        ]
else:
    filtered_df = df  # empty


# ================= TABLE =================
st.subheader("Incident Table")
st.dataframe(filtered_df, use_container_width=True)


# ================= CHARTS =================
if not filtered_df.empty:
    st.markdown("---")
    st.header("📊 Cyber Incident Analytics Dashboard")

    col1, col2 = st.columns(2)

    # ----------------------------------------------------------
    # Chart 1 — Severity Bar Chart
    # ----------------------------------------------------------
    with col1:
        st.subheader("Severity Distribution")
        st.bar_chart(filtered_df["Severity"].value_counts())

    # ----------------------------------------------------------
    # Chart 2 — Category Bar Chart
    # ----------------------------------------------------------
    with col2:
        st.subheader("Incident Categories")
        st.bar_chart(filtered_df["Category"].value_counts())

    # ----------------------------------------------------------
    # SECOND ROW — PIE CHARTS
    # ----------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Severity Breakdown (Pie Chart)")
        pie1 = filtered_df["Severity"].value_counts().plot.pie(
            autopct="%1.1f%%", ylabel="", figsize=(5, 5)
        ).get_figure()
        st.pyplot(pie1)

    with col4:
        st.subheader("Status Breakdown (Pie Chart)")
        pie2 = filtered_df["Status"].value_counts().plot.pie(
            autopct="%1.1f%%", ylabel="", figsize=(5, 5)
        ).get_figure()
        st.pyplot(pie2)
else:
    st.info("Not enough incident data to show charts yet.")


# ==========================================================
#                CRUD SECTION (CREATE / UPDATE / DELETE)
# ==========================================================
st.markdown("---")
st.header("✏️ Manage Incidents (CRUD)")

crud_tab_create, crud_tab_update, crud_tab_delete = st.tabs(
    ["➕ Create Incident", "📝 Update Status", "🗑️ Delete Incident"]
)

# -------------------------- CREATE --------------------------
with crud_tab_create:
    st.subheader("Create New Incident")

    col_a, col_b = st.columns(2)

    with col_a:
        new_id = st.number_input(
            "Incident ID",
            min_value=1,
            step=1,
            help="Must be unique (primary key)."
        )
        new_category = st.text_input("Category (e.g. Phishing, Malware)")
        new_severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"]
        )

    with col_b:
        new_status = st.selectbox(
            "Status",
            ["open", "investigating", "resolved", "closed"]
        )
        new_description = st.text_area("Description")
        # Simple timestamp (ISO format)
        timestamp_default = datetime.now().isoformat(timespec="seconds")
        new_timestamp = st.text_input(
            "Timestamp",
            value=timestamp_default,
            help="ISO format or any text date."
        )

    if st.button("Create Incident"):
        if not new_category or not new_description:
            st.warning("Please fill in Category and Description.")
        else:
            try:
                db.execute_query(
                    """
                    INSERT INTO cyber_incidents
                        (incident_id, timestamp, severity, category, status, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(new_id),
                        new_timestamp,
                        new_severity,
                        new_category,
                        new_status,
                        new_description,
                    ),
                )
                st.success(f"Incident {int(new_id)} created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating incident: {e}")


# -------------------------- UPDATE STATUS --------------------------
with crud_tab_update:
    st.subheader("Update Incident Status")

    if df.empty:
        st.info("No incidents available to update.")
    else:
        incident_ids = df["ID"].tolist()
        selected_id = st.selectbox("Select Incident ID", incident_ids)
        new_status = st.selectbox(
            "New Status",
            ["open", "investigating", "resolved", "closed"]
        )

        if st.button("Update Status"):
            try:
                db.execute_query(
                    "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
                    (new_status, int(selected_id)),
                )
                st.success(f"Incident {int(selected_id)} updated to '{new_status}'.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating incident: {e}")


# -------------------------- DELETE --------------------------
with crud_tab_delete:
    st.subheader("Delete Incident")

    if df.empty:
        st.info("No incidents available to delete.")
    else:
        incident_ids = df["ID"].tolist()
        delete_id = st.selectbox("Select Incident ID to delete", incident_ids)

        danger = st.checkbox(
            "I understand this will permanently delete the incident.",
            value=False
        )

        if st.button("Delete Incident", type="primary", disabled=not danger):
            try:
                db.execute_query(
                    "DELETE FROM cyber_incidents WHERE incident_id = ?",
                    (int(delete_id),),
                )
                st.success(f"Incident {int(delete_id)} deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting incident: {e}")
