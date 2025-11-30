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

st.title("🤖 Ultra-Fast Multi-Domain AI Assistant (FREE)")
st.caption("Powered by Phi-3 Mini (local model via Ollama)")

# ------------------------------------------------------
# SUPER FAST AI FUNCTION (phi3:mini)
# ------------------------------------------------------
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


# ------------------------------------------------------
# Conversation memory (LIMITED FOR SPEED)
# ------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Only keep last 3 messages for faster inference
conversation_context = st.session_state.messages[-3:]

# Display conversation
for msg in conversation_context:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------------------------------------
# Chat input
# ------------------------------------------------------
prompt = st.chat_input("Ask the AI Assistant...")

if prompt:

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Store message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate fast AI reply
    reply = ask_local_ai(
        f"You are an expert in cyber security, data analytics, and IT operations. Respond clearly.\nUser: {prompt}"
    )

    # Display AI message
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Store AI response
    st.session_state.messages.append({"role": "assistant", "content": reply})
