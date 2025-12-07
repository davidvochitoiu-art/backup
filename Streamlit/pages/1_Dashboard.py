import streamlit as st
import pandas as pd

from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="Dashboard", layout="wide")

# -----------------------------------
# LOGIN CHECK
# -----------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in first.")
    st.switch_page("Home.py")

st.title("📊 Multi-Domain Intelligence Dashboard")

# -----------------------------------
# DATABASE
# -----------------------------------
db = DatabaseManager("DATA/intelligence_platform.db")

# --------------------------------------------------------------
# SECTION 1 — CYBERSECURITY INCIDENTS
# --------------------------------------------------------------

st.header("🛡️ Cybersecurity Incidents")
st.write("""
This section provides an overview of the cybersecurity incidents recorded in the system.  
It includes key details such as incident category, severity levels, status, and descriptions.  
A severity-level chart helps visualize how critical the incidents are.
""")

rows_incidents = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)

incidents = [SecurityIncident(*row) for row in rows_incidents]

df_incidents = pd.DataFrame([{
    "ID": inc.get_id(),
    "Category": inc.get_incident_type(),
    "Severity": inc.get_severity(),
    "Status": inc.get_status(),
    "Description": inc.get_description(),
    "Severity Level (1–4)": inc.get_severity_level()
} for inc in incidents])

st.subheader("Incident Records")
st.dataframe(df_incidents, use_container_width=True)

st.subheader("Severity Level Distribution")
st.bar_chart(df_incidents["Severity Level (1–4)"])


# --------------------------------------------------------------
# SECTION 2 — DATASETS OVERVIEW
# --------------------------------------------------------------

st.header("📂 Datasets Overview")
st.write("""
This section displays metadata about datasets uploaded to the system.  
It shows each dataset’s size estimate, number of rows/columns, uploader information,  
and upload date. This helps analysts understand available data resources.
""")

rows_datasets = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)

datasets = [Dataset(*row) for row in rows_datasets]

df_datasets = pd.DataFrame([{
    "ID": ds.get_id(),
    "Name": ds.get_name(),
    "Rows": ds.get_rows(),
    "Columns": ds.get_columns(),
    "Uploaded By": ds.get_uploaded_by(),
    "Upload Date": ds.get_upload_date(),
    "Estimated Size (MB)": ds.calculate_size_mb()
} for ds in datasets])

st.subheader("Dataset Records")
st.dataframe(df_datasets, use_container_width=True)

st.subheader("Dataset Size Estimate (MB)")
st.bar_chart(df_datasets["Estimated Size (MB)"])


# --------------------------------------------------------------
# SECTION 3 — IT TICKETS
# --------------------------------------------------------------

st.header("💼 IT Support Tickets")
st.write("""
This section provides insights into IT support tickets created in the system.  
It includes priority levels, assigned personnel, and ticket status.  
A priority chart helps visualize the distribution of workload.
""")

rows_tickets = db.fetch_all(
    "SELECT ticket_id, priority, description, status, assigned_to FROM it_tickets"
)

tickets = [
    ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4]
    )
    for row in rows_tickets
]

df_tickets = pd.DataFrame([{
    "ID": tk.get_id(),
    "Title": tk.get_title(),
    "Priority": tk.get_priority(),
    "Status": tk.get_status(),
    "Assigned To": tk.get_assigned_to()
} for tk in tickets])

st.subheader("Ticket Records")
st.dataframe(df_tickets, use_container_width=True)

st.subheader("Priority Distribution")
st.bar_chart(df_tickets["Priority"])
