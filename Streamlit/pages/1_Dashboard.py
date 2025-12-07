import streamlit as st
import pandas as pd
import plotly.express as px

# Import your real DB functions
from app.data.incidents import (
    get_all_incidents,
    create_incident,
    update_incident_status,
    delete_incident,
)
from app.data.datasets import (
    get_all_datasets,
    create_dataset,
    delete_dataset,
)
from app.data.tickets import (
    get_all_tickets,
    create_ticket,
    update_ticket_status,
    delete_ticket,
)

# -------------------------------------------------------------------
# PAGE CONFIG + SIMPLE LIGHT PROFESSIONAL THEME
# -------------------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.markdown(
    """
<style>
    .stApp {
        background-color: #f5f7fb;
    }
    .big-title {
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        color: #222831;
        padding: 4px 0 10px 0;
    }
    .sub-title {
        text-align: center;
        color: #4b5563;
        font-size: 15px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='big-title'>📊 Multi-Domain Intelligence Dashboard</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Monitor Cyber Incidents, Datasets and IT Tickets in one place.</div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# AUTO RISK CLASSIFICATION HELPERS
# -------------------------------------------------------------------
def classify_incident(severity):
    severity = str(severity).lower()
    if "critical" in severity:
        return "Critical"
    if "high" in severity:
        return "High"
    if "medium" in severity:
        return "Medium"
    return "Low"


def classify_ticket(priority):
    priority = str(priority).lower()
    if "critical" in priority:
        return "Critical"
    if "high" in priority:
        return "High"
    if "medium" in priority:
        return "Medium"
    return "Low"


# -------------------------------------------------------------------
# LOGIN GUARD
# -------------------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view this page.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

st.success(f"Welcome, **{st.session_state.username}**! 👋")


# -------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------------
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_AI_Assistant.py", label="🤖 AI Assistant")

    st.divider()
    st.header("Choose View")
    table_choice = st.selectbox(
        "Select domain:",
        ["Cyber Incidents", "Datasets Metadata", "IT Tickets"],
    )

# -------------------------------------------------------------------
# LOAD REAL DATA FROM SQL
# -------------------------------------------------------------------
incidents = get_all_incidents()
datasets = get_all_datasets()
tickets = get_all_tickets()

# Convert to DataFrames
df_incidents = pd.DataFrame(
    incidents,
    columns=[
        "incident_id",
        "timestamp",
        "severity",
        "category",
        "status",
        "description",
    ],
)

df_datasets = pd.DataFrame(
    datasets,
    columns=[
        "dataset_id",
        "name",
        "rows",
        "columns",
        "uploaded_by",
        "upload_date",
    ],
)

df_tickets = pd.DataFrame(
    tickets,
    columns=[
        "ticket_id",
        "priority",
        "description",
        "status",
        "assigned_to",
        "created_at",
        "resolution_time_hours",
    ],
)

# Add risk category columns
if not df_incidents.empty:
    df_incidents["risk_category"] = df_incidents["severity"].apply(classify_incident)
if not df_tickets.empty:
    df_tickets["risk_category"] = df_tickets["priority"].apply(classify_ticket)

# -------------------------------------------------------------------
# CYBER INCIDENTS
# -------------------------------------------------------------------
if table_choice == "Cyber Incidents":
    st.subheader("🛡 Cyber Incidents")

    st.markdown(
        """
**What this section shows:**  
All recorded cybersecurity incidents, their severity, status and timing.

**Why it matters:**  
Helps analysts spot spikes in severe incidents, understand attack patterns, and prioritise response.
"""
    )

    st.dataframe(df_incidents, use_container_width=True)

    if not df_incidents.empty:
        # Ensure proper datetime
        df_incidents["timestamp"] = pd.to_datetime(
            df_incidents["timestamp"], errors="coerce"
        )

        col1, col2 = st.columns(2)

        # ---------- Donut: Risk Distribution ----------
        with col1:
            st.markdown("### 🎯 Incident Risk Distribution")
            severity_counts = df_incidents["risk_category"].value_counts()

            fig = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                hole=0.55,
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A donut chart showing the proportion of Low, Medium, High and Critical incidents.

**Why this matters:**  
It gives a quick visual overview of how many high-risk incidents demand urgent attention.
"""
                )

        # ---------- Time-based chart 1: Incidents per Day ----------
        with col2:
            st.markdown("### 📅 Incidents per Day")
            incidents_per_day = (
                df_incidents.groupby(df_incidents["timestamp"].dt.date)
                .size()
                .rename("count")
            )
            st.line_chart(incidents_per_day)

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A line chart showing how many incidents occurred each day.

**Why this matters:**  
Helps identify spikes in activity, attack waves, or days where monitoring needs to be strengthened.
"""
                )

        st.markdown("### 📊 Incidents per Month")
        incidents_per_month = (
            df_incidents.groupby(df_incidents["timestamp"].dt.to_period("M"))
            .size()
            .rename("count")
        )
        incidents_per_month.index = incidents_per_month.index.astype(str)
        st.bar_chart(incidents_per_month)

        with st.expander("ℹ More about this chart"):
            st.markdown(
                """
**What this is:**  
A monthly view of total incident volume.

**Why this matters:**  
Shows longer-term trends and is useful for reporting to management or planning resources.
"""
            )

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage Cyber Incidents")

    # CREATE
    with st.expander("➕ Add New Incident"):
        new_id = st.number_input("Incident ID", step=1)
        new_timestamp = st.text_input("Timestamp (YYYY-MM-DD)")
        new_severity = st.selectbox(
            "Severity", ["Low", "Medium", "High", "Critical"]
        )
        new_category = st.text_input("Category")
        new_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
        new_desc = st.text_area("Description")

        if st.button("Create Incident"):
            create_incident(
                new_id,
                new_timestamp,
                new_severity,
                new_category,
                new_status,
                new_desc,
            )
            st.success("Incident created.")
            st.rerun()

    # UPDATE
    with st.expander("🔄 Update Incident Status"):
        if not df_incidents.empty:
            select_id = st.selectbox("Select Incident ID", df_incidents["incident_id"])
            new_status2 = st.selectbox("New Status", ["Open", "In Progress", "Closed"])

            if st.button("Update Status"):
                update_incident_status(select_id, new_status2)
                st.success("Incident updated.")
                st.rerun()
        else:
            st.info("No incidents available to update.")

    # DELETE
    with st.expander("🗑 Delete Incident"):
        if not df_incidents.empty:
            del_id = st.selectbox(
                "Select Incident to Delete", df_incidents["incident_id"]
            )

            if st.button("Delete Incident"):
                delete_incident(del_id)
                st.warning("Incident deleted.")
                st.rerun()
        else:
            st.info("No incidents available to delete.")

# -------------------------------------------------------------------
# DATASETS METADATA
# -------------------------------------------------------------------
elif table_choice == "Datasets Metadata":
    st.subheader("📦 Datasets Metadata")

    st.markdown(
        """
**What this section shows:**  
All datasets registered in the platform, including size, owner and upload date.

**Why it matters:**  
Helps manage data governance, storage usage and identify large datasets that may need archiving or optimisation.
"""
    )

    st.dataframe(df_datasets, use_container_width=True)

    if not df_datasets.empty:
        col1, col2 = st.columns(2)

        # ----- BAR CHART -----
        with col1:
            st.markdown("### 📊 Rows per Dataset")
            st.bar_chart(df_datasets.set_index("name")["rows"])

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A bar chart showing the number of rows for each dataset.

**Why this matters:**  
Highlights large datasets that may impact performance or require governance decisions.
"""
                )

        # ----- LINE CHART -----
        with col2:
            st.markdown("### 📈 Dataset Size Trend Over Time")
            df_datasets["upload_date"] = pd.to_datetime(
                df_datasets["upload_date"], errors="coerce"
            )
            dataset_trend = (
                df_datasets.groupby(df_datasets["upload_date"].dt.date)["rows"]
                .sum()
                .rename("total_rows")
            )
            st.line_chart(dataset_trend)

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A time series showing the total number of dataset rows uploaded per day.

**Why this matters:**  
Shows how data volume is growing over time and supports storage/capacity planning.
"""
                )

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage Datasets")

    with st.expander("➕ Add New Dataset"):
        d_id = st.number_input("Dataset ID", step=1)
        d_name = st.text_input("Dataset Name")
        d_rows = st.number_input("Rows", step=1)
        d_cols = st.number_input("Columns", step=1)
        d_user = st.text_input("Uploaded By")
        d_date = st.text_input("Upload Date (YYYY-MM-DD)")

        if st.button("Create Dataset"):
            create_dataset(d_id, d_name, d_rows, d_cols, d_user, d_date)
            st.success("Dataset created.")
            st.rerun()

    with st.expander("🗑 Delete Dataset"):
        if not df_datasets.empty:
            del_dataset = st.selectbox(
                "Select Dataset ID", df_datasets["dataset_id"]
            )

            if st.button("Delete Dataset"):
                delete_dataset(del_dataset)
                st.warning("Dataset deleted.")
                st.rerun()
        else:
            st.info("No datasets available to delete.")

# -------------------------------------------------------------------
# IT TICKETS
# -------------------------------------------------------------------
elif table_choice == "IT Tickets":
    st.subheader("🧰 IT Tickets")

    st.markdown(
        """
**What this section shows:**  
All IT support tickets, their priority, status, and resolution time.

**Why it matters:**  
Helps IT managers track workload, delays and recurring issues affecting users.
"""
    )

    st.dataframe(df_tickets, use_container_width=True)

    if not df_tickets.empty:
        df_tickets["created_at"] = pd.to_datetime(
            df_tickets["created_at"], errors="coerce"
        )

        col1, col2 = st.columns(2)

        # ----- Donut: Priority / Risk -----
        with col1:
            st.markdown("### 🎯 Ticket Risk Distribution")
            priority_counts = df_tickets["risk_category"].value_counts()

            fig_t = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                hole=0.55,
            )
            fig_t.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_t, use_container_width=True)

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A donut chart showing how many tickets are Low, Medium, High or Critical.

**Why this matters:**  
Reveals whether the service desk is dealing with mostly urgent issues or routine tasks.
"""
                )

        # ----- Time-based: Tickets per Day -----
        with col2:
            st.markdown("### 📅 Tickets Created per Day")
            tickets_per_day = (
                df_tickets.groupby(df_tickets["created_at"].dt.date)
                .size()
                .rename("count")
            )
            st.line_chart(tickets_per_day)

            with st.expander("ℹ More about this chart"):
                st.markdown(
                    """
**What this is:**  
A line chart showing how many tickets were opened each day.

**Why this matters:**  
Helps identify busy periods, recurring peaks and potential staffing issues.
"""
                )

        # Resolution time trend (you already had this – kept & improved label)
        st.markdown("### ⏱ Average Resolution Time Trend")
        ticket_trend = (
            df_tickets.groupby(df_tickets["created_at"].dt.date)[
                "resolution_time_hours"
            ]
            .mean()
            .rename("avg_resolution_hours")
        )
        st.line_chart(ticket_trend)

        with st.expander("ℹ More about this chart"):
            st.markdown(
                """
**What this is:**  
A time series showing the average number of hours taken to resolve tickets each day.

**Why this matters:**  
Highlights improvements or regressions in service desk performance and helps spot bottlenecks.
"""
            )

    # -----------------------------
    # CRUD Section
    # -----------------------------
    st.divider()
    st.header("🛠 Manage IT Tickets")

    with st.expander("➕ Create New Ticket"):
        t_id = st.number_input("Ticket ID", step=1)
        t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        t_desc = st.text_area("Description")
        t_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
        t_assigned = st.text_input("Assigned To")
        t_created = st.text_input("Created At (YYYY-MM-DD)")
        t_res = st.number_input("Resolution Time (hrs)", step=1)

        if st.button("Create Ticket"):
            create_ticket(
                t_id,
                t_priority,
                t_desc,
                t_status,
                t_assigned,
                t_created,
                t_res,
            )
            st.success("Ticket created.")
            st.rerun()

    with st.expander("🔄 Update Ticket Status"):
        if not df_tickets.empty:
            t_select = st.selectbox("Select Ticket ID", df_tickets["ticket_id"])
            t_new_status = st.selectbox("New Status", ["Open", "In Progress", "Closed"])

            if st.button("Update Ticket"):
                update_ticket_status(t_select, t_new_status)
                st.success("Ticket updated.")
                st.rerun()
        else:
            st.info("No tickets available to update.")

    with st.expander("🗑 Delete Ticket"):
        if not df_tickets.empty:
            del_t = st.selectbox("Select Ticket", df_tickets["ticket_id"])

            if st.button("Delete Ticket"):
                delete_ticket(del_t)
                st.warning("Ticket deleted.")
                st.rerun()
        else:
            st.info("No tickets available to delete.")

# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------
st.divider()
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("Home.py")
