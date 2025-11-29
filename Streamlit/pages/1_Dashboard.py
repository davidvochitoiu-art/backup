import streamlit as st
import pandas as pd

# Import your real DB functions
from app.data.incidents import get_all_incidents, create_incident, update_incident_status, delete_incident
from app.data.datasets import get_all_datasets, create_dataset, delete_dataset
from app.data.tickets import get_all_tickets, create_ticket, update_ticket_status, delete_ticket

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

# =============================
#     CYBER INCIDENTS
# =============================
if table_choice == "Cyber Incidents":
    st.subheader("🛡 Cyber Incidents Table")
    st.dataframe(df_incidents)

    # ----- BAR CHART -----
    st.subheader("Severity Count (Bar Chart)")
    severity_counts = df_incidents["severity"].value_counts()
    st.bar_chart(severity_counts)

    # ----- LINE CHART -----
    st.subheader("Incidents Over Time (Line Chart)")
    df_incidents["timestamp"] = pd.to_datetime(df_incidents["timestamp"], errors="coerce")
    incidents_per_day = df_incidents.groupby(df_incidents["timestamp"].dt.date).size()
    st.line_chart(incidents_per_day)

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage Cyber Incidents")

    # CREATE
    with st.expander("➕ Add New Incident"):
        new_id = st.number_input("Incident ID", step=1)
        new_timestamp = st.text_input("Timestamp (YYYY-MM-DD)")
        new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        new_category = st.text_input("Category")
        new_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
        new_desc = st.text_area("Description")

        if st.button("Create Incident"):
            create_incident(new_id, new_timestamp, new_severity, new_category, new_status, new_desc)
            st.success("Incident created! Refresh page.")

    # UPDATE
    with st.expander("🔄 Update Incident Status"):
        select_id = st.selectbox("Select Incident ID", df_incidents["incident_id"])
        new_status2 = st.selectbox("New Status", ["Open", "In Progress", "Closed"])

        if st.button("Update Status"):
            update_incident_status(select_id, new_status2)
            st.success("Incident status updated! Refresh page.")

    # DELETE
    with st.expander("🗑 Delete Incident"):
        del_id = st.selectbox("Select Incident to Delete", df_incidents["incident_id"])

        if st.button("Delete Incident"):
            delete_incident(del_id)
            st.error("Incident deleted! Refresh page.")


# =============================
#     DATASETS
# =============================
elif table_choice == "Datasets Metadata":
    st.subheader("📦 Datasets Metadata Table")
    st.dataframe(df_datasets)

    # ----- BAR CHART -----
    st.subheader("Rows per Dataset (Bar Chart)")
    st.bar_chart(df_datasets.set_index("name")["rows"])

    # ----- LINE CHART -----
    st.subheader("Dataset Size Trend Over Time (Line Chart)")
    df_datasets["upload_date"] = pd.to_datetime(df_datasets["upload_date"], errors="coerce")
    dataset_trend = df_datasets.groupby(df_datasets["upload_date"].dt.date)["rows"].sum()
    st.line_chart(dataset_trend)

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage Datasets")

    # CREATE
    with st.expander("➕ Add New Dataset"):
        d_id = st.number_input("Dataset ID", step=1)
        d_name = st.text_input("Dataset Name")
        d_rows = st.number_input("Rows", step=1)
        d_cols = st.number_input("Columns", step=1)
        d_user = st.text_input("Uploaded By")
        d_date = st.text_input("Upload Date (YYYY-MM-DD)")

        if st.button("Create Dataset"):
            create_dataset(d_id, d_name, d_rows, d_cols, d_user, d_date)
            st.success("Dataset created! Refresh page.")

    # DELETE
    with st.expander("🗑 Delete Dataset"):
        del_dataset = st.selectbox("Select Dataset ID", df_datasets["dataset_id"])

        if st.button("Delete Dataset"):
            delete_dataset(del_dataset)
            st.error("Dataset deleted! Refresh page.")


# =============================
#          IT TICKETS
# =============================
elif table_choice == "IT Tickets":
    st.subheader("🧰 IT Tickets Table")
    st.dataframe(df_tickets)

    # ----- BAR CHART -----
    st.subheader("Priority Count (Bar Chart)")
    priority_counts = df_tickets["priority"].value_counts()
    st.bar_chart(priority_counts)

    # ----- LINE CHART -----
    st.subheader("Resolution Time Trend (Line Chart)")
    df_tickets["created_at"] = pd.to_datetime(df_tickets["created_at"], errors="coerce")
    ticket_trend = df_tickets.groupby(df_tickets["created_at"].dt.date)["resolution_time_hours"].mean()
    st.line_chart(ticket_trend)

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage IT Tickets")

    # CREATE
    with st.expander("➕ Create New Ticket"):
        t_id = st.number_input("Ticket ID", step=1)
        t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        t_desc = st.text_area("Description")
        t_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
        t_assigned = st.text_input("Assigned To")
        t_created = st.text_input("Created At (YYYY-MM-DD)")
        t_res = st.number_input("Resolution Time (hrs)", step=1)

        if st.button("Create Ticket"):
            create_ticket(t_id, t_priority, t_desc, t_status, t_assigned, t_created, t_res)
            st.success("Ticket created! Refresh page.")

    # UPDATE
    with st.expander("🔄 Update Ticket Status"):
        t_select = st.selectbox("Select Ticket ID", df_tickets["ticket_id"])
        t_new_status = st.selectbox("New Status", ["Open", "In Progress", "Closed"])

        if st.button("Update Ticket"):
            update_ticket_status(t_select, t_new_status)
            st.success("Ticket status updated! Refresh page.")

    # DELETE
    with st.expander("🗑 Delete Ticket"):
        del_t = st.selectbox("Select Ticket", df_tickets["ticket_id"])

        if st.button("Delete Ticket"):
            delete_ticket(del_t)
            st.error("Ticket deleted! Refresh page.")


# -----------------------------
# Logout
# -----------------------------
st.divider()
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("Home.py")
