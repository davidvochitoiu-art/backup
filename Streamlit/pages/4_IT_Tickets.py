import streamlit as st
import pandas as pd
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="IT Tickets", layout="wide")

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("💼 IT Support Ticket Analysis")

db = DatabaseManager("DATA/intelligence_platform.db")

# ============== LOAD TICKETS ==============
rows = db.fetch_all("""
    SELECT ticket_id, priority, description, status, assigned_to
    FROM it_tickets
""")

tickets = [
    ITTicket(
        ticket_id=row[0],
        title=row[2],         # description becomes title
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


# ================= FILTER SECTION =================
st.subheader("Filters")

if df.empty:
    filtered_df = df
    st.info("No ticket data available yet.")
else:
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


# ================= TABLE SECTION =================
st.subheader("Ticket Records")
st.dataframe(filtered_df, use_container_width=True)


# ================= CHARTS SECTION =================
if not filtered_df.empty:
    st.subheader("Ticket Priority Breakdown")
    st.bar_chart(filtered_df["Priority"].value_counts())

    st.subheader("Status Breakdown")
    st.bar_chart(filtered_df["Status"].value_counts())


st.markdown("---")
st.header("✏️ Manage IT Tickets (CRUD)")

# =====================================================
#               CREATE / UPDATE / DELETE TABS
# =====================================================
crud_tab_create, crud_tab_update, crud_tab_delete = st.tabs(
    ["➕ Create Ticket", "📝 Update Ticket Status", "🗑️ Delete Ticket"]
)


# -----------------------------------------------------
#                     CREATE TICKET
# -----------------------------------------------------
with crud_tab_create:
    st.subheader("Create New Ticket")

    colA, colB = st.columns(2)

    with colA:
        new_id = st.number_input("Ticket ID", min_value=1, step=1)
        new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        new_assigned = st.text_input("Assigned To (optional)")

    with colB:
        new_status = st.selectbox(
            "Status",
            ["Open", "In Progress", "On Hold", "Closed"]
        )
        new_title = st.text_input("Title")
        new_description = st.text_area("Description")

    if st.button("Create Ticket"):
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
                        None  # no resolution time yet
                    ),
                )
                st.success(f"Ticket {int(new_id)} created successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating ticket: {e}")


# -----------------------------------------------------
#               UPDATE TICKET STATUS
# -----------------------------------------------------
with crud_tab_update:
    st.subheader("Update Ticket Status")

    if df.empty:
        st.info("No tickets available.")
    else:
        ticket_ids = df["ID"].tolist()
        selected_ticket = st.selectbox("Select Ticket ID", ticket_ids)

        new_status = st.selectbox(
            "New Status",
            ["Open", "In Progress", "On Hold", "Closed"]
        )

        if st.button("Update Status"):
            try:
                db.execute_query(
                    "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
                    (new_status, int(selected_ticket))
                )
                st.success(f"Ticket {int(selected_ticket)} updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating ticket: {e}")


# -----------------------------------------------------
#                     DELETE TICKET
# -----------------------------------------------------
with crud_tab_delete:
    st.subheader("Delete Ticket")

    if df.empty:
        st.info("No tickets available to delete.")
    else:
        ticket_ids = df["ID"].tolist()
        delete_id = st.selectbox("Select Ticket ID to Delete", ticket_ids)

        confirm = st.checkbox(
            "I understand this will permanently delete the ticket.",
            value=False
        )

        if st.button("Delete Ticket", type="primary", disabled=not confirm):
            try:
                db.execute_query(
                    "DELETE FROM it_tickets WHERE ticket_id = ?",
                    (int(delete_id),)
                )
                st.success(f"Ticket {int(delete_id)} deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting ticket: {e}")
