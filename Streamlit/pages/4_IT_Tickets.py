import streamlit as st
import pandas as pd
from app.services.database_manager import DatabaseManager
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="IT Tickets", layout="wide")

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("💼 IT Support Ticket Analysis")

db = DatabaseManager("DATA/intelligence_platform.db")

# Load tickets
rows = db.fetch_all("""
    SELECT ticket_id, priority, description, status, assigned_to
    FROM it_tickets
""")

tickets = [
    ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4]
    )
    for row in rows
]

df = pd.DataFrame([{
    "ID": t.get_id(),
    "Title": t.get_title(),
    "Priority": t.get_priority(),
    "Status": t.get_status(),
    "Assigned To": t.get_assigned_to()
} for t in tickets])

# -----------------------------------------------------
# FILTER SECTION
# -----------------------------------------------------
st.subheader("Filters")

col1, col2, col3 = st.columns(3)

with col1:
    priority_filter = st.selectbox(
        "Filter by Priority",
        ["All"] + sorted(df["Priority"].unique().tolist())
    )

with col2:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + sorted(df["Status"].unique().tolist())
    )

with col3:
    assigned_filter = st.selectbox(
        "Filter by Assigned To",
        ["All"] + sorted(df["Assigned To"].unique().tolist())
    )

# Apply filters
filtered_df = df.copy()

if priority_filter != "All":
    filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]

if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Status"] == status_filter]

if assigned_filter != "All":
    filtered_df = filtered_df[filtered_df["Assigned To"] == assigned_filter]

# -----------------------------------------------------
# TABLE SECTION
# -----------------------------------------------------
st.subheader("Ticket Records")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------------------------------
# CHARTS SECTION
# -----------------------------------------------------
st.subheader("Ticket Priority Breakdown")
st.bar_chart(filtered_df["Priority"].value_counts())

st.subheader("Ticket Status Breakdown")
st.bar_chart(filtered_df["Status"].value_counts())


st.markdown("---")
st.header("📊 IT Ticket Analytics Dashboard")

col1, col2 = st.columns(2)

# ----------------------------------------------------------
# Chart 1 — Priority Bar Chart
# ----------------------------------------------------------
with col1:
    st.subheader("Ticket Priority Distribution")
    st.bar_chart(filtered_df["Priority"].value_counts())

# ----------------------------------------------------------
# Chart 2 — Status Bar Chart
# ----------------------------------------------------------
with col2:
    st.subheader("Ticket Status Distribution")
    st.bar_chart(filtered_df["Status"].value_counts())

# ----------------------------------------------------------
# SECOND ROW — PIE CHARTS
# ----------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Priority Breakdown (Pie Chart)")
    fig = filtered_df["Priority"].value_counts().plot.pie(
        autopct="%1.1f%%", ylabel="", figsize=(5, 5)
    ).get_figure()
    st.pyplot(fig)

with col4:
    st.subheader("Status Breakdown (Pie Chart)")
    fig2 = filtered_df["Status"].value_counts().plot.pie(
        autopct="%1.1f%%", ylabel="", figsize=(5, 5)
    ).get_figure()
    st.pyplot(fig2)
