import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="IT Tickets", layout="wide")

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("💼 IT Support Ticket Analysis")

# ---------------- DATABASE LOAD ----------------
db = DatabaseManager("DATA/intelligence_platform.db")

rows = db.fetch_all(
    """
    SELECT ticket_id, priority, description, status, assigned_to
    FROM it_tickets
    """
)

tickets = [
    ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4],
    )
    for row in rows
]

df = pd.DataFrame(
    [
        {
            "ID": t.get_id(),
            "Title": t.get_title(),
            "Priority": t.get_priority(),
            "Status": t.get_status(),
            "Assigned To": t.get_assigned_to(),
        }
        for t in tickets
    ]
)

# ---------------- FILTER SECTION ----------------
st.subheader("Filters")

if df.empty:
    st.info("No ticket data available yet.")
    filtered_df = df
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All"] + sorted(df["Priority"].unique().tolist()),
            key="ticket_filter_priority",
        )

    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + sorted(df["Status"].unique().tolist()),
            key="ticket_filter_status",
        )

    with col3:
        assigned_filter = st.selectbox(
            "Filter by Assigned To",
            ["All"] + sorted(df["Assigned To"].unique().tolist()),
            key="ticket_filter_assigned",
        )

    filtered_df = df.copy()

    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    if assigned_filter != "All":
        filtered_df = filtered_df[filtered_df["Assigned To"] == assigned_filter]

# ---------------- TABLE SECTION ----------------
st.subheader("Ticket Records")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- BASIC CHARTS ----------------
if not filtered_df.empty:
    st.subheader("Ticket Priority Breakdown")
    st.bar_chart(filtered_df["Priority"].value_counts())

    st.subheader("Status Breakdown")
    st.bar_chart(filtered_df["Status"].value_counts())
else:
    st.info("Not enough ticket data for charts yet.")

# ---------------- NEW HEATMAP (REPLACE RADAR) ----------------
st.subheader("🔥 Staff Workload by Priority – Heatmap")

heat_df = (
    df.groupby(["Assigned To", "Priority"])
    .size()
    .reset_index(name="Count")
)

if not heat_df.empty:
    pivot = heat_df.pivot(
        index="Assigned To",
        columns="Priority",
        values="Count"
    ).fillna(0)

    fig_heatmap = px.imshow(
        pivot,
        labels=dict(x="Priority", y="Assigned To", color="Ticket Count"),
        title="Heatmap – Ticket Distribution by Staff and Priority",
        text_auto=True,
        aspect="auto",
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("Not enough data for heatmap yet.")

# ---------------- CRUD SECTION ----------------
st.markdown("---")
st.header("✏️ Manage IT Tickets (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create Ticket", "📝 Update Ticket Status", "🗑️ Delete Ticket"]
)

# ---------------- CREATE ----------------
with tab_create:
    st.subheader("Create a New IT Ticket")

    col_a, col_b = st.columns(2)

    with col_a:
        new_id = st.number_input(
            "Ticket ID", min_value=1, step=1, key="ticket_create_id"
        )
        new_priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High", "Critical"],
            key="ticket_create_priority",
        )
        new_assigned = st.text_input(
            "Assigned To (optional)",
            key="ticket_create_assigned",
        )

    with col_b:
        new_status = st.selectbox(
            "Status",
            ["Open", "In Progress", "On Hold", "Closed"],
            key="ticket_create_status",
        )
        new_title = st.text_input("Title", key="ticket_create_title")
        new_description = st.text_area(
            "Description", key="ticket_create_description"
        )

    if st.button("Create Ticket", key="ticket_create_button"):
        if not new_title or not new_description:
            st.warning("Please fill in Title and Description.")
        else:
            try:
                db.execute_query(
                    """
                    INSERT INTO it_tickets 
                        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(new_id),
                        new_priority,
                        new_description,
                        new_status,
                        new_assigned,
                        datetime.now().isoformat(timespec="seconds"),
                        None,
                    ),
                )
                st.success(f"Ticket {int(new_id)} created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating ticket: {e}")

# ---------------- UPDATE ----------------
with tab_update:
    st.subheader("Update Ticket Status")

    if df.empty:
        st.info("No tickets available to update.")
    else:
        ticket_ids = df["ID"].tolist()
        selected_ticket = st.selectbox(
            "Select Ticket ID",
            ticket_ids,
            key="ticket_update_id",
        )

        upd_status = st.selectbox(
            "New Status",
            ["Open", "In Progress", "On Hold", "Closed"],
            key="ticket_update_status",
        )

        if st.button("Update Ticket", key="ticket_update_button"):
            try:
                db.execute_query(
                    "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
                    (upd_status, int(selected_ticket)),
                )
                st.success(f"Ticket {int(selected_ticket)} updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating ticket: {e}")

# ---------------- DELETE ----------------
with tab_delete:
    st.subheader("Delete Ticket")

    if df.empty:
        st.info("No tickets available to delete.")
    else:
        ticket_ids = df["ID"].tolist()
        del_id = st.selectbox(
            "Select Ticket ID",
            ticket_ids,
            key="ticket_delete_id",
        )

        confirm = st.checkbox(
            "I confirm I want to permanently delete this ticket",
            key="ticket_delete_confirm",
        )

        if st.button(
            "Delete Ticket",
            type="primary",
            disabled=not confirm,
            key="ticket_delete_button",
        ):
            try:
                db.execute_query(
                    "DELETE FROM it_tickets WHERE ticket_id = ?",
                    (int(del_id),),
                )
                st.success(f"Ticket {int(del_id)} deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting ticket: {e}")
