import streamlit as st
import pandas as pd
import plotly.express as px

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="Dashboard", layout="wide")

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("📊 Multi-Domain Intelligence Platform – Dashboard")

# ---------------- DATABASE ----------------
db = DatabaseManager("DATA/intelligence_platform.db")

# Cyber incidents
inc_rows = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)
incidents = [
    SecurityIncident(
        incident_id=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4],
    )
    for row in inc_rows
]

df_inc = pd.DataFrame(
    [
        {
            "ID": i.get_id(),
            "Category": i.get_incident_type(),
            "Severity": i.get_severity(),
            "Status": i.get_status(),
        }
        for i in incidents
    ]
)

# Datasets
data_rows = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)
datasets = [Dataset(*row) for row in data_rows]

df_data = pd.DataFrame(
    [
        {
            "ID": d.get_id(),
            "Name": d.get_name(),
            "Rows": d.get_rows(),
            "Columns": d.get_columns(),
            "Uploaded By": d.get_uploaded_by(),
            "Upload Date": d.get_upload_date(),
            "Estimated Size (MB)": d.calculate_size_mb(),
        }
        for d in datasets
    ]
)

# IT Tickets
ticket_rows = db.fetch_all(
    "SELECT ticket_id, priority, description, status, assigned_to FROM it_tickets"
)
tickets = [
    ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4],
    )
    for row in ticket_rows
]

df_tickets = pd.DataFrame(
    [
        {
            "ID": t.get_id(),
            "Priority": t.get_priority(),
            "Status": t.get_status(),
            "Assigned To": t.get_assigned_to(),
        }
        for t in tickets
    ]
)

# ---------------- KPI CARDS ----------------
st.subheader("📌 Key Metrics Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Cyber Incidents", len(df_inc))

with col2:
    critical_count = sum(
        1 for i in incidents if i.get_severity().lower() == "critical"
    )
    st.metric("Critical Incidents", critical_count)

with col3:
    st.metric("Total Datasets", len(df_data))

with col4:
    st.metric("Total IT Tickets", len(df_tickets))

st.markdown("---")

# ---------------- 3-DOMAIN VISUAL OVERVIEW ----------------
st.header("📊 Domain Analytics Overview")

# --------- CYBER INCIDENTS ----------
st.subheader("🛡 Cybersecurity Overview")

if not df_inc.empty:
    colA, colB = st.columns(2)

    with colA:
        st.write("**Incident Severity Distribution**")
        fig_sev = px.bar(
            df_inc["Severity"].value_counts(),
            title="Severity Distribution",
            labels={"value": "Count", "index": "Severity"},
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    with colB:
        st.write("**Incident Categories**")
        fig_cat = px.bar(
            df_inc["Category"].value_counts(),
            title="Category Distribution",
            labels={"value": "Count", "index": "Category"},
        )
        st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("No incident data available.")

st.markdown("---")

# --------- DATASETS ----------
st.subheader("📂 Dataset Overview")

if not df_data.empty:
    colA, colB = st.columns(2)

    with colA:
        st.write("**Dataset Size (MB)**")
        fig_size = px.bar(
            df_data,
            x="Name",
            y="Estimated Size (MB)",
            title="Dataset Size Comparison",
        )
        st.plotly_chart(fig_size, use_container_width=True)

    with colB:
        st.write("**Rows per Dataset**")
        fig_rows = px.line(
            df_data,
            x="Name",
            y="Rows",
            markers=True,
            title="Dataset Row Count Overview",
        )
        st.plotly_chart(fig_rows, use_container_width=True)
else:
    st.info("No dataset information found.")

st.markdown("---")

# --------- IT TICKETS ----------
st.subheader("💼 IT Ticket Overview")

if not df_tickets.empty:
    colA, colB = st.columns(2)

    with colA:
        st.write("**Priority Breakdown**")
        fig_priority = px.bar(
            df_tickets["Priority"].value_counts(),
            title="Ticket Priority Distribution",
            labels={"value": "Count", "index": "Priority"},
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    with colB:
        st.write("**Status Breakdown**")
        fig_status = px.bar(
            df_tickets["Status"].value_counts(),
            title="Ticket Status Distribution",
            labels={"value": "Count", "index": "Status"},
        )
        st.plotly_chart(fig_status, use_container_width=True)
else:
    st.info("No ticket data available.")

st.markdown("---")

st.success("Dashboard loaded successfully!")
