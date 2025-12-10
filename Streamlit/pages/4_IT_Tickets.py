import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from app.services.database_manager import DatabaseManager
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="IT Tickets", layout="wide")

# ---------- LOGIN CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("💼 IT Support Tickets")

# ---------- LOAD DATA ----------
db = DatabaseManager("DATA/intelligence_platform.db")

rows = db.fetch_all(
    "SELECT ticket_id, priority, description, status, assigned_to FROM it_tickets"
)

tickets = []
for row in rows:
    t = ITTicket(
        ticket_id=row[0],
        title=row[2],
        priority=row[1],
        status=row[3],
        assigned_to=row[4],
    )
    tickets.append(t)

ticket_records = []
for t in tickets:
    ticket_records.append(
        {
            "ID": t.get_id(),
            "Title": t.get_title(),
            "Priority": t.get_priority(),
            "Status": t.get_status(),
            "Assigned To": t.get_assigned_to(),
        }
    )

df = pd.DataFrame(ticket_records)

# ---------- FILTERS ----------
st.subheader("Filters")

if df.empty:
    st.info("No tickets yet. Use the forms below to create one.")
    filtered_df = df
else:
    f1, f2, f3 = st.columns(3)

    with f1:
        pri_options = ["All"] + sorted(df["Priority"].unique().tolist())
        priority_filter = st.selectbox(
            "Priority",
            pri_options,
            key="ticket_filter_priority",
        )

    with f2:
        stat_options = ["All"] + sorted(df["Status"].unique().tolist())
        status_filter = st.selectbox(
            "Status",
            stat_options,
            key="ticket_filter_status",
        )

    with f3:
        ass_options = ["All"] + sorted(df["Assigned To"].unique().tolist())
        assigned_filter = st.selectbox(
            "Assigned To",
            ass_options,
            key="ticket_filter_assigned",
        )

    filtered_df = df.copy()
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    if assigned_filter != "All":
        filtered_df = filtered_df[filtered_df["Assigned To"] == assigned_filter]

# ---------- TABLE ----------
st.subheader("Ticket Records")
st.dataframe(filtered_df, use_container_width=True)

# ---------- BASIC CHARTS ----------
if not filtered_df.empty:
    st.subheader("Priority Breakdown")
    st.bar_chart(filtered_df["Priority"].value_counts())

    st.subheader("Status Breakdown")
    st.bar_chart(filtered_df["Status"].value_counts())
else:
    st.info("Not enough tickets to show charts yet.")

# ---------- HEATMAP ----------
st.subheader("🔥 Staff Workload by Priority (Heatmap)")

heat_df = (
    df.groupby(["Assigned To", "Priority"])
    .size()
    .reset_index(name="Count")
)

if not heat_df.empty:
    pivot = heat_df.pivot(
        index="Assigned To",
        columns="Priority",
        values="Count",
    ).fillna(0)

    fig_heat = px.imshow(
        pivot,
        labels={"x": "Priority", "y": "Assigned To", "color": "Ticket Count"},
        title="Ticket Distribution by Staff and Priority",
        text_auto=True,
        aspect="auto",
    )
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Not enough data for heatmap yet.")

# ---------- CRUD ----------
st.markdown("---")
st.header("✏️ Manage Tickets (CRUD)")

tab_create, tab_update, tab_delete = st.tabs(
    ["➕ Create", "📝 Update Status", "🗑️ Delete"]
)

# CREATE
with tab_create:
    st.subheader("Create New Ticket")

    c1, c2 = st.columns(2)

    with c1:
        new_id = st.number_input(
            "Ticket ID",
            min_value=1,
            step=1,
            key="ticket_create_id",
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

    with c2:
        new_status = st.selectbox(
            "Status",
            ["Open", "In Progress", "On Hold", "Closed"],
            key="ticket_create_status",
        )
        new_title = st.text_input(
            "Title",
            key="ticket_create_title",
        )
        new_desc = st.text_area(
            "Description",
            key="ticket_create_description",
        )

    if st.button("Create Ticket", key="ticket_create_button"):
        if not new_title or not new_desc:
            st.warning("Please fill in title and description.")
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
                        new_desc,
                        new_status,
                        new_assigned,
                        datetime.now().isoformat(timespec="seconds"),
                        None,
                    ),
                )
                st.success(f"Ticket {int(new_id)} created.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating ticket: {e}")

# UPDATE
with tab_update:
    st.subheader("Update Ticket Status")

    if df.empty:
        st.info("No tickets to update.")
    else:
        id_list = df["ID"].tolist()
        upd_id = st.selectbox(
            "Select Ticket ID",
            id_list,
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
                    (upd_status, int(upd_id)),
                )
                st.success(f"Ticket {int(upd_id)} updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating ticket: {e}")

# DELETE
with tab_delete:
    st.subheader("Delete Ticket")

    if df.empty:
        st.info("No tickets to delete.")
    else:
        id_list = df["ID"].tolist()
        del_id = st.selectbox(
            "Select Ticket ID to delete",
            id_list,
            key="ticket_delete_id",
        )

        confirm = st.checkbox(
            "I confirm I want to permanently delete this ticket.",
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
                st.success(f"Ticket {int(del_id)} deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting ticket: {e}")
