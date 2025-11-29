import streamlit as st
import pandas as pd

# Import your real DB functions
from app.data.incidents import get_all_incidents
from app.data.datasets import get_all_datasets
from app.data.tickets import get_all_tickets

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# -----------------------------
# Login guard
# -----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

st.title("📊 Real Data Dashboard")
st.success(f"Welcome, {st.session_state.username}!")

# -----------------------------
# Load REAL data from SQL
# -----------------------------
incidents = get_all_incidents()
datasets = get_all_datasets()
tickets = get_all_tickets()

# Convert to DataFrames
df_incidents = pd.DataFrame(incidents, columns=[
    "incident_id", "timestamp", "severity", "category", "status", "description"
])

df_datasets = pd.DataFrame(datasets, columns=[
    "dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date"
])

df_tickets = pd.DataFrame(tickets, columns=[
    "ticket_id", "priority", "description", "status", "assigned_to",
    "created_at", "resolution_time_hours"
])

# -----------------------------
# Sidebar selection
# -----------------------------
with st.sidebar:
    st.header("Choose Table")
    table_choice = st.selectbox(
        "Select table to display:",
        ["Cyber Incidents", "Datasets Metadata", "IT Tickets"]
    )

# -----------------------------
# Display selected table + charts
# -----------------------------
if table_choice == "Cyber Incidents":
    st.subheader("🛡 Cyber Incidents Table")
    st.dataframe(df_incidents)

    st.subheader("Severity Count (Bar Chart)")
    severity_counts = df_incidents["severity"].value_counts()
    st.bar_chart(severity_counts)

elif table_choice == "Datasets Metadata":
    st.subheader("📦 Datasets Metadata Table")
    st.dataframe(df_datasets)

    st.subheader("Rows per Dataset (Bar Chart)")
    st.bar_chart(df_datasets.set_index("name")["rows"])

elif table_choice == "IT Tickets":
    st.subheader("🧰 IT Tickets Table")
    st.dataframe(df_tickets)

    st.subheader("Priority Count (Bar Chart)")
    priority_counts = df_tickets["priority"].value_counts()
    st.bar_chart(priority_counts)

# -----------------------------
# Logout
# -----------------------------
st.divider()
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("Home.py")
