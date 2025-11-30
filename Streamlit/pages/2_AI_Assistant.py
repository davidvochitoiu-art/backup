import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Assistant", page_icon="🤖")

# -----------------------------
# Login guard
# -----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to use the AI assistant.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_AI_Assistant.py", label="🤖 AI Assistant")

st.title("🤖 Multi-Domain AI Assistant (FREE)")
st.caption("Powered by Llama 3:8B (local model via Ollama)")

# ------------------------------------------------------
# AI Function (uses local Ollama model llama3:8b)
# ------------------------------------------------------
def ask_local_ai(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3:8b", "prompt": prompt},
        stream=True
    )

    full_reply = ""

    # Read Ollama stream chunk by chunk
    for line in r.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    full_reply += data["response"]
            except:
                pass

    return full_reply.strip()


# ------------------------------------------------------
# Conversation memory
# ------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are an expert assistant specialising in:
- Cyber Security
- Data Analytics
- IT Operations
Provide clear and detailed support for incidents, datasets, and tickets."""
        }
    ]

# Display conversation
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ------------------------------------------------------
# Chat input
# ------------------------------------------------------
prompt = st.chat_input("Ask the AI Assistant...")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get reply from local Llama 3:8b
    reply = ask_local_ai(prompt)

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
