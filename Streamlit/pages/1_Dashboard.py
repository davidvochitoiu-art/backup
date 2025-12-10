import streamlit as st
import pandas as pd
import plotly.express as px

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

# I just keep it wide so charts look nicer
st.set_page_config(page_title="Dashboard", layout="wide")

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("📊 Multi-Domain Intelligence Platform")

# ---------------- LOAD DATA FROM DB ----------------
db = DatabaseManager("DATA/intelligence_platform.db")

# Load incidents
inc_rows = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)
incidents = []
for row in inc_rows:
    incident = SecurityIncident(
        incident_id=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4],
    )
    incidents.append(incident)

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

# Load datasets
data_rows = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)
datasets = []
for row in data_rows:
    d = Dataset(
        dataset_id=row[0],
        name=row[1],
        rows=row[2],
        columns=row[3],
        uploaded_by=row[4],
        upload_date=row[5],
    )
    datasets.append(d)

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

# Load tickets
ticket_rows = db.fetch_all(
    "SELECT ticket_id, priority, description, status, assigned_to FROM it_tickets"
)
tickets = []
for row in ticket_rows:
    t = ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4],
    )
    tickets.append(t)

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
st.subheader("📌 Quick Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents", len(df_inc))

with col2:
    crit_count = 0
    for inc in incidents:
        if inc.get_severity() and inc.get_severity().lower() == "critical":
            crit_count += 1
    st.metric("Critical Incidents", crit_count)

with col3:
    st.metric("Total Datasets", len(df_data))

with col4:
    st.metric("Total IT Tickets", len(df_tickets))

st.markdown("---")

# ---------------- CYBER SECTION ----------------
st.header("🛡 Cybersecurity Overview")

if not df_inc.empty:
    c1, c2 = st.columns(2)

    with c1:
        st.write("**Incident Severity Distribution**")
        sev_counts = df_inc["Severity"].value_counts()
        fig_sev = px.bar(
            sev_counts,
            title="Severity Distribution",
            labels={"index": "Severity", "value": "Count"},
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    with c2:
        st.write("**Incident Category Distribution**")
        cat_counts = df_inc["Category"].value_counts()
        fig_cat = px.bar(
            cat_counts,
            title="Category Distribution",
            labels={"index": "Category", "value": "Count"},
        )
        st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("No incident data available yet.")

st.markdown("---")

# ---------------- DATASET SECTION ----------------
st.header("📂 Dataset Overview")

if not df_data.empty:
    d1, d2 = st.columns(2)

    with d1:
        st.write("**Dataset Size in MB**")
        fig_size = px.bar(
            df_data,
            x="Name",
            y="Estimated Size (MB)",
            title="Dataset Sizes",
        )
        st.plotly_chart(fig_size, use_container_width=True)

    with d2:
        st.write("**Rows per Dataset**")
        fig_rows = px.line(
            df_data,
            x="Name",
            y="Rows",
            markers=True,
            title="Row Count per Dataset",
        )
        st.plotly_chart(fig_rows, use_container_width=True)
else:
    st.info("No datasets stored yet.")

st.markdown("---")

# ---------------- IT TICKET SECTION ----------------
st.header("💼 IT Tickets Overview")

if not df_tickets.empty:
    t1, t2 = st.columns(2)

    with t1:
        st.write("**Ticket Priority Breakdown**")
        fig_pri = px.bar(
            df_tickets["Priority"].value_counts(),
            title="Ticket Priorities",
            labels={"index": "Priority", "value": "Count"},
        )
        st.plotly_chart(fig_pri, use_container_width=True)

    with t2:
        st.write("**Ticket Status Breakdown**")
        fig_stat = px.bar(
            df_tickets["Status"].value_counts(),
            title="Ticket Statuses",
            labels={"index": "Status", "value": "Count"},
        )
        st.plotly_chart(fig_stat, use_container_width=True)
else:
    st.info("No ticket data available yet.")

st.success("Dashboard loaded.")
