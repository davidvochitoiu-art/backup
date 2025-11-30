import streamlit as st
import openai
from openai import OpenAI


st.set_page_config(page_title="AI Assistant", page_icon="🤖")

# -----------------------------
# Login guard
# -----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to use the AI assistant.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

# Connect to OpenAI using secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_AI_Assistant.py", label="🤖 AI Assistant")

st.title("🤖 Multi-Domain AI Assistant")
st.caption("Powered by OpenAI GPT-4o")

# Initialise conversation history
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

# Display past messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ask the AI Assistant...")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Stream assistant reply
    reply = ""
    with st.chat_message("assistant"):
        container = st.empty()

        for chunk in client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            temperature=1,
            stream=True
        ):
            if chunk.choices[0].delta.content:
                reply += chunk.choices[0].delta.content
                container.markdown(reply + "▌")

        container.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
