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

st.title("📊 Multi-Domain Dashboard")

# -----------------------------------
# DATABASE
# -----------------------------------
db = DatabaseManager("DATA/intelligence_platform.db")

# ==============================================================
#                     CYBER INCIDENTS (OOP)
# ==============================================================

rows_incidents = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)

incidents = [
    SecurityIncident(*row)
    for row in rows_incidents
]

df_incidents = pd.DataFrame([{
    "ID": inc.get_id(),
    "Category": inc.get_incident_type(),
    "Severity": inc.get_severity(),
    "Status": inc.get_status(),
    "Description": inc.get_description(),
    "Level": inc.get_severity_level()
} for inc in incidents])

st.subheader("Cybersecurity Incidents")
st.dataframe(df_incidents)
st.bar_chart(df_incidents["Level"])


# ==============================================================
#                         DATASETS (OOP)
# ==============================================================

rows_datasets = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)

datasets = [
    Dataset(*row)
    for row in rows_datasets
]

df_datasets = pd.DataFrame([{
    "ID": ds.get_id(),
    "Name": ds.get_name(),
    "Rows": ds.get_rows(),
    "Columns": ds.get_columns(),
    "Uploaded By": ds.get_uploaded_by(),
    "Upload Date": ds.get_upload_date(),
    "Estimated Size (MB)": ds.calculate_size_mb()
} for ds in datasets])

st.subheader("Datasets Overview")
st.dataframe(df_datasets)


# ==============================================================
#                        IT TICKETS (OOP)
# ==============================================================

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

st.subheader("IT Tickets Overview")
st.dataframe(df_tickets)
