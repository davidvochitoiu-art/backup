import streamlit as st
import requests
import json

# ================================
#         IMPORT DATABASE
# ================================
from app.data.incidents import get_all_incidents
from app.data.datasets import get_all_datasets
from app.data.tickets import get_all_tickets

st.set_page_config(page_title="AI Assistant", page_icon="🤖")

# ================================
#        LOGIN CHECK
# ================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to use the AI assistant.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

# ================================
#   OLLAMA LOCAL AI FUNCTION
# ================================
def ask_local_ai(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi3:mini", "prompt": prompt},
        stream=True
    )

    full_reply = ""
    for line in r.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    full_reply += data["response"]
            except:
                pass

    return full_reply.strip()


# ================================
#     DATABASE → TEXT FORMATTER
# ================================
def format_table(table, title):
    if not table:
        return f"No entries found for {title}."
    text = f"--- {title} ---\n"
    for row in table[:8]:  # safety: only show first 8
        text += str(row) + "\n"
    return text


# ================================
#       TOOL FUNCTIONS
# ================================
def run_tool(user_message):

    msg = user_message.lower()

    # Cybersecurity queries
    if "incident" in msg or "cyber" in msg:
        data = get_all_incidents()
        return format_table(data, "Cyber Incidents")

    # Data science queries
    if "dataset" in msg or "data set" in msg:
        data = get_all_datasets()
        return format_table(data, "Datasets Metadata")

    # IT ticket queries
    if "ticket" in msg or "it support" in msg or "helpdesk" in msg:
        data = get_all_tickets()
        return format_table(data, "IT Tickets")

    # If no tool matched → return None
    return None


# ================================
#     SIDEBAR NAVIGATION
# ================================
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_AI_Assistant.py", label="🤖 AI Assistant")

st.title("🤖 Advanced Multi-Domain AI Assistant")
st.caption("Powered by local Phi-3 (FREE) + Database-Aware Intelligence")


# ================================
#     CONVERSATION MEMORY
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ================================
#        CHAT INPUT
# ================================
prompt = st.chat_input("Ask the AI Assistant...")

if prompt:

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # ====================================
    #        TOOL ACTIVATION CHECK
    # ====================================
    tool_output = run_tool(prompt)

    if tool_output:
        # AI uses tool → return data
        with st.chat_message("assistant"):
            st.markdown(f"📊 **I fetched live data from the database:**\n\n```\n{tool_output}\n```")

        st.session_state.messages.append({
            "role": "assistant",
            "content": tool_output
        })

    else:
        # Normal AI reasoning
        full_prompt = (
            "You are an expert assistant in Cybersecurity, Data Science, and IT Operations.\n"
            "If the user asks for data, call the correct tool by describing which domain it belongs to.\n\n"
            f"User said: {prompt}\n"
        )

        reply = ask_local_ai(full_prompt)

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })
