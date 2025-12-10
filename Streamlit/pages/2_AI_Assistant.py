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

st.title("🤖 AI Assistant")

# ------------------------------
# DATABASE & AI ENGINE
# ------------------------------
db = DatabaseManager("DATA/intelligence_platform.db")
ai = AIAssistant(model="phi3:mini")

# ------------------------------
# CHAT HISTORY
# ------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================================================
#           LOAD DATA FROM DATABASE USING OOP MODELS
# ==============================================================

def load_data():
    # Incidents
    rows_inc = db.fetch_all(
        "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
    )
    incidents = [SecurityIncident(*row) for row in rows_inc]

    # Datasets
    rows_ds = db.fetch_all(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
    )
    datasets = [Dataset(*row) for row in rows_ds]

    # Tickets
    rows_tk = db.fetch_all(
        "SELECT ticket_id, priority, description, status, assigned_to FROM it_tickets"
    )
    tickets = [
        ITTicket(
            ticket_id=row[0],
            title=row[2],
            priority=row[1],
            status=row[3],
            assigned_to=row[4],
        ) for row in rows_tk
    ]

    return incidents, datasets, tickets

incidents, datasets, tickets = load_data()

# ==============================================================
#         OPTIONAL INTELLIGENCE CONTEXT FOR ANALYTICS ANSWERS
# ==============================================================

def build_context():
    context = "### SYSTEM SUMMARY\n"

    # --- INCIDENTS ---
    context += "\n## Cybersecurity Incidents\n"
    if incidents:
        total = len(incidents)
        critical = sum(1 for i in incidents if i.get_severity().lower() == "critical")
        top_cat = max([i.get_incident_type() for i in incidents], key=lambda x: 
                      [i.get_incident_type() for i in incidents].count(x))

        context += (
            f"- Total incidents: {total}\n"
            f"- Critical: {critical}\n"
            f"- Most common category: {top_cat}\n"
        )
    else:
        context += "- No incident data.\n"

    # --- DATASETS ---
    context += "\n## Datasets\n"
    if datasets:
        largest = max(datasets, key=lambda d: d.get_rows() or 0)
        context += (
            f"- Total datasets: {len(datasets)}\n"
            f"- Largest dataset: {largest.get_name()} ({largest.get_rows()} rows)\n"
        )
    else:
        context += "- No dataset data.\n"

    # --- TICKETS ---
    context += "\n## IT Tickets\n"
    if tickets:
        total = len(tickets)
        closed = sum(1 for t in tickets if t.get_status().lower() == "closed")
        staff = [t.get_assigned_to() for t in tickets if t.get_assigned_to()]
        top_staff = max(set(staff), key=staff.count) if staff else "N/A"

        context += (
            f"- Total tickets: {total}\n"
            f"- Closed tickets: {closed}\n"
            f"- Staff with most assignments: {top_staff}\n"
        )
    else:
        context += "- No ticket data.\n"

    context += (
        "\n### Instructions\n"
        "You may use the data above if the question relates to incidents, datasets, "
        "or IT tickets. If the user's question is general or unrelated, answer normally.\n"
    )

    return context


# ==============================================================
#  USER SETTING: USE CONTEXT OR NOT?
# ==============================================================

use_context = st.checkbox(
    "Use system analytics context (optional)", 
    value=True,
    help="Turn off to ask completely general questions."
)

# ==============================================================
#  DISPLAY CHAT HISTORY
# ==============================================================

for role, msg in st.session_state.chat_history:
    st.chat_message(role).markdown(msg)

# ==============================================================
#  USER INPUT
# ==============================================================

prompt = st.chat_input("Ask me anything…")

if prompt:
    # show user message immediately
    st.session_state.chat_history.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    # build final prompt
    if use_context:
        full_prompt = build_context() + "\nUser: " + prompt
    else:
        full_prompt = prompt  # fully open domain

    with st.spinner("AI is thinking…"):
        response = ai.ask(full_prompt)

    # show response
    st.session_state.chat_history.append(("assistant", response))
    st.chat_message("assistant").markdown(response)
