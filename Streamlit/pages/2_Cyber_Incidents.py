import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident

st.set_page_config(page_title="Cyber Incidents", layout="wide")

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("🛡️ Cybersecurity Incidents Analysis")

# ---------------- DATABASE ----------------
db = DatabaseManager("DATA/intelligence_platform.db")

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
        description=row[4],
    )
    for row in rows
]

df = pd.DataFrame(
    [
        {
            "ID": inc.get_id(),
            "Category": inc.get_incident_type(),
            "Severity": inc.get_severity(),
            "Status": inc.get_status(),
            "Description": inc.get_description(),
            "Severity Level (1–4)": inc.get_severity_level(),
        }
        for inc in incidents
    ]
)

# ---------------- FILTERS ----------------
st.subheader("Filters")

if df.empty:
    st.info("No incidents found yet. Use the CRUD section below to create one.")
    filtered_df = df
else:
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All"] + sorted(df["Severity"].dropna().unique().tolist()),
        key="incident_filter_severity",
    )
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + sorted(df["Status"].dropna().unique().tolist()),
        key="incident_filter_status",
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

# ---------------- TABLE ----------------
st.subheader("Incident Table")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- CHARTS ----------------
if not filtered_df.empty:
    st.markdown("---")
    st.header("📊 Cyber Incident Analytics")

    col1, col2 = st.columns(2)

    # Severity bar chart
    with col1:
        st.subheader("Severity Distribution")
        st.bar_chart(filtered_df["Severity"].value_counts())

    # Category bar chart
    with col2:
        st.subheader("Incident Categories")
        st.bar_chart(filtered_df["Category"].value_counts())

    # Advanced Bubble Chart
    st.subheader("🔥 Severity vs Category Bubble Chart")
    bubble_df = (
        filtered_df.groupby(["Category", "Severity"])
        .size()
        .reset_index(name="Count")
    )

    fig_bubble = px.scatter(
        bubble_df,
        x="Category",
        y="Severity",
        size="Count",
        color="Severity",
        title="Bubble Chart – Severity vs Category vs Frequency",
        size_max=60,
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
else:
    st.info("Not enough incident data to show charts yet.")

# ---------------- CRUD SECTION ----------------
st.markdown("---")
st.header("✏️ Manage Incidents (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create Incident", "📝 Update Status", "🗑️ Delete Incident"]
)

# CREATE
with tab_create:
    st.subheader("Create New Incident")

    col_a, col_b = st.columns(2)

    with col_a:
        new_id = st.number_input(
            "Incident ID",
            min_value=1,
            step=1,
            help="Must be unique (primary key).",
            key="incident_create_id",
        )
        new_category = st.text_input("Category (e.g. Phishing, Malware)")
        new_severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"],
            key="incident_create_severity",
        )

    with col_b:
        new_status = st.selectbox(
            "Status",
            ["open", "investigating", "resolved", "closed"],
            key="incident_create_status",
        )
        new_description = st.text_area("Description")
        new_timestamp = datetime.now().isoformat(timespec="seconds")

    if st.button("Create Incident", key="incident_create_button"):
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

# UPDATE
with tab_update:
    st.subheader("Update Incident Status")

    if df.empty:
        st.info("No incidents available to update.")
    else:
        incident_ids = df["ID"].tolist()
        selected_id = st.selectbox(
            "Select Incident ID",
            incident_ids,
            key="incident_update_id",
        )
        upd_status = st.selectbox(
            "New Status",
            ["open", "investigating", "resolved", "closed"],
            key="incident_update_status",
        )

        if st.button("Update Status", key="incident_update_button"):
            try:
                db.execute_query(
                    "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
                    (upd_status, int(selected_id)),
                )
                st.success(
                    f"Incident {int(selected_id)} updated to '{upd_status}'."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error updating incident: {e}")

# DELETE
with tab_delete:
    st.subheader("Delete Incident")

    if df.empty:
        st.info("No incidents available to delete.")
    else:
        incident_ids = df["ID"].tolist()
        delete_id = st.selectbox(
            "Select Incident ID to delete",
            incident_ids,
            key="incident_delete_id",
        )

        danger = st.checkbox(
            "I understand this will permanently delete the incident.",
            value=False,
            key="incident_delete_confirm",
        )

        if st.button(
            "Delete Incident",
            type="primary",
            disabled=not danger,
            key="incident_delete_button",
        ):
            try:
                db.execute_query(
                    "DELETE FROM cyber_incidents WHERE incident_id = ?",
                    (int(delete_id),),
                )
                st.success(
                    f"Incident {int(delete_id)} deleted successfully."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting incident: {e}")
