import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident

st.set_page_config(page_title="Cyber Incidents", layout="wide")

# ---------- LOGIN CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("🛡 Cybersecurity Incidents")

# ---------- LOAD DATA ----------
db = DatabaseManager("DATA/intelligence_platform.db")

rows = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)

incidents = []
for row in rows:
    inc = SecurityIncident(
        incident_id=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4],
    )
    incidents.append(inc)

data_for_df = []
for inc in incidents:
    data_for_df.append(
        {
            "ID": inc.get_id(),
            "Category": inc.get_incident_type(),
            "Severity": inc.get_severity(),
            "Status": inc.get_status(),
            "Description": inc.get_description(),
            "Severity Level (1–4)": inc.get_severity_level(),
        }
    )

df = pd.DataFrame(data_for_df)

# ---------- FILTERS ----------
st.subheader("Filters")

if df.empty:
    st.info("No incidents found yet. Use the forms below to create one.")
    filtered_df = df
else:
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        severity_options = ["All"]
        if "Severity" in df.columns:
            severity_options += sorted(df["Severity"].dropna().unique().tolist())
        severity_filter = st.selectbox(
            "Filter by Severity",
            severity_options,
            key="incident_filter_severity",
        )

    with col_f2:
        status_options = ["All"]
        if "Status" in df.columns:
            status_options += sorted(df["Status"].dropna().unique().tolist())
        status_filter = st.selectbox(
            "Filter by Status",
            status_options,
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

# ---------- TABLE ----------
st.subheader("Incident Table")
st.dataframe(filtered_df, use_container_width=True)

# ---------- CHARTS ----------
if not filtered_df.empty:
    st.markdown("---")
    st.header("📊 Incident Analytics")

    c1, c2 = st.columns(2)

    with c1:
        st.write("**Severity Distribution**")
        sev_counts = filtered_df["Severity"].value_counts()
        st.bar_chart(sev_counts)

    with c2:
        st.write("**Category Distribution**")
        cat_counts = filtered_df["Category"].value_counts()
        st.bar_chart(cat_counts)

    # Bubble chart to show category + severity + count
    st.subheader("🔥 Bubble Chart – Severity vs Category")
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
        title="Severity vs Category (Bubble = Frequency)",
        size_max=60,
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
else:
    st.info("Not enough data to show charts yet.")

# ---------- CRUD ----------
st.markdown("---")
st.header("✏️ Manage Incidents (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create", "📝 Update Status", "🗑️ Delete"]
)

# CREATE
with tab_create:
    st.subheader("Create New Incident")

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        new_id = st.number_input(
            "Incident ID",
            min_value=1,
            step=1,
            key="incident_create_id",
        )
        new_category = st.text_input(
            "Category (e.g. Phishing, Malware)",
            key="incident_create_category",
        )
        new_severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"],
            key="incident_create_severity",
        )

    with col_c2:
        new_status = st.selectbox(
            "Status",
            ["open", "investigating", "resolved", "closed"],
            key="incident_create_status",
        )
        new_description = st.text_area(
            "Description",
            key="incident_create_description",
        )
        new_timestamp = datetime.now().isoformat(timespec="seconds")

    if st.button("Create Incident", key="incident_create_button"):
        if not new_category or not new_description:
            st.warning("Please fill in category and description.")
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
                st.success(f"Incident {int(new_id)} created.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating incident: {e}")

# UPDATE
with tab_update:
    st.subheader("Update Incident Status")

    if df.empty:
        st.info("No incidents to update.")
    else:
        id_list = df["ID"].tolist()
        selected_id = st.selectbox(
            "Select Incident ID",
            id_list,
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
                st.success(f"Incident {int(selected_id)} updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating incident: {e}")

# DELETE
with tab_delete:
    st.subheader("Delete Incident")

    if df.empty:
        st.info("No incidents to delete.")
    else:
        id_list = df["ID"].tolist()
        delete_id = st.selectbox(
            "Select Incident ID to delete",
            id_list,
            key="incident_delete_id",
        )

        confirm = st.checkbox(
            "I understand this will permanently delete the incident.",
            key="incident_delete_confirm",
        )

        if st.button(
            "Delete Incident",
            type="primary",
            disabled=not confirm,
            key="incident_delete_button",
        ):
            try:
                db.execute_query(
                    "DELETE FROM cyber_incidents WHERE incident_id = ?",
                    (int(delete_id),),
                )
                st.success(f"Incident {int(delete_id)} deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting incident: {e}")
