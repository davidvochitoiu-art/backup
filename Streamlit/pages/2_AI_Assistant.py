import streamlit as st
import pandas as pd

from app.services.database_manager import DatabaseManager
from app.services.ai_assistant import AIAssistant

from app.models.security_incident import SecurityIncident
from app.models.dataset import Dataset
from app.models.it_ticket import ITTicket

st.set_page_config(page_title="AI Assistant", layout="wide")

# ------------------------------
# LOGIN CHECK
# ------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("🤖 AI Assistant (OOP Version)")

# ------------------------------
# DATABASE & AI ENGINE
# ------------------------------
db = DatabaseManager("DATA/intelligence_platform.db")
ai = AIAssistant(model="phi3:mini")

# ------------------------------
# CHAT HISTORY SETUP
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==============================================================
#            LOAD DATA FROM DATABASE USING OOP MODELS
# ==============================================================

# INCIDENTS
rows_inc = db.fetch_all(
    "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
)
incidents = [SecurityIncident(*row) for row in rows_inc]

# DATASETS
rows_ds = db.fetch_all(
    "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
)
datasets = [Dataset(*row) for row in rows_ds]

# TICKETS
rows_tk = db.fetch_all(
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
    for row in rows_tk
]


# ==============================================================
#         BUILD INTELLIGENT CONTEXT FOR THE AI MODEL
# ==============================================================

def build_context():
    # -------------------------------------------
    # Build intelligent analytics for the AI
    # -------------------------------------------
    context = "### SYSTEM INTELLIGENCE CONTEXT\n"

    # ==========================================================
    # INCIDENT ANALYTICS
    # ==========================================================
    context += "\n## Cybersecurity Incidents Summary\n"

    if incidents:
        total_inc = len(incidents)
        critical_inc = sum(1 for i in incidents if i.get_severity().lower() == "critical")
        high_inc = sum(1 for i in incidents if i.get_severity().lower() == "high")

        # Most common category
        cats = [i.get_incident_type() for i in incidents]
        top_cat = max(set(cats), key=cats.count)

        context += (
            f"- Total incidents: {total_inc}\n"
            f"- Critical incidents: {critical_inc}\n"
            f"- High severity incidents: {high_inc}\n"
            f"- Most common incident category: {top_cat}\n"
        )

        # List top 5 severe incidents
        top_severe = sorted(
            incidents,
            key=lambda i: i.get_severity_level(),
            reverse=True
        )[:5]

        context += "\n### Top Severe Incidents\n"
        for inc in top_severe:
            context += (
                f"- [{inc.get_severity()}] {inc.get_incident_type()} "
                f"(Status: {inc.get_status()}) — {inc.get_description()}\n"
            )
    else:
        context += "- No incident data available.\n"

    # ==========================================================
    # DATASET ANALYTICS
    # ==========================================================
    context += "\n## Dataset Analytics\n"

    if datasets:
        largest = max(datasets, key=lambda d: d.get_rows() or 0)

        context += (
            f"- Total datasets: {len(datasets)}\n"
            f"- Largest dataset: {largest.get_name()} "
            f"({largest.get_rows()} rows, {largest.get_columns()} cols)\n"
        )

        # Row count distribution
        row_counts = [d.get_rows() for d in datasets if d.get_rows() is not None]
        if row_counts:
            avg_rows = sum(row_counts) / len(row_counts)
            context += f"- Average dataset row count: {avg_rows:.2f}\n"
    else:
        context += "- No datasets available.\n"

    # ==========================================================
    # TICKET ANALYTICS
    # ==========================================================
    context += "\n## IT Tickets Summary\n"

    if tickets:
        total_tk = len(tickets)
        closed_tk = sum(1 for t in tickets if t.get_status().lower() == "closed")

        staff_list = [t.get_assigned_to() for t in tickets if t.get_assigned_to()]
        if staff_list:
            top_worker = max(set(staff_list), key=staff_list.count)
        else:
            top_worker = "N/A"

        context += (
            f"- Total tickets: {total_tk}\n"
            f"- Closed tickets: {closed_tk}\n"
            f"- Staff with most tickets: {top_worker}\n"
        )
    else:
        context += "- No ticket data available.\n"

    # ==========================================================
    # FINAL INSTRUCTIONS FOR THE AI
    # ==========================================================
    context += (
        "\n### Instructions\n"
        "You are an expert analyst AI assistant.\n"
        "Use the analytics above to answer the user's question clearly and intelligently.\n"
        "Provide explanations, insights, and recommendations when helpful.\n"
        "Do not just repeat the data — analyse it.\n"
    )

    return context


# ==============================================================
#                 DISPLAY CHAT HISTORY
# ==============================================================

for role, msg in st.session_state.chat_history:
    st.chat_message(role).markdown(msg)


# ==============================================================
#                    USER INPUT BOX
# ==============================================================

prompt = st.chat_input("Ask the AI anything...")

if prompt:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    # Build full prompt including context
    full_prompt = build_context() + "\nUser question: " + prompt

    with st.spinner("AI is thinking..."):
        ai_response = ai.ask(full_prompt)

    # Show AI response
    st.session_state.chat_history.append(("assistant", ai_response))
    st.chat_message("assistant").markdown(ai_response)
