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
    context = "\n=== SYSTEM DATA CONTEXT ===\n"

    # INCIDENTS
    context += "\nCyber Incidents:\n"
    for inc in incidents:
        context += f"- [{inc.get_severity()}] {inc.get_incident_type()} | Status: {inc.get_status()}\n"

    # DATASETS
    context += "\nDatasets:\n"
    for ds in datasets:
        context += f"- {ds.get_name()} | Rows: {ds.get_rows()}, Columns: {ds.get_columns()}\n"

    # TICKETS
    context += "\nIT Tickets:\n"
    for tk in tickets:
        context += f"- {tk.get_title()} | Priority: {tk.get_priority()} | Status: {tk.get_status()}\n"

    context += "\nUse this data to answer the user's question.\n"
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
