import streamlit as st

# import your DB functions
from app.data.users import create_user, verify_user, get_user

st.set_page_config(page_title="Login / Register", layout="centered")

# session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Real Database Login System")

# If logged in → send to dashboard
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")

login_tab, register_tab = st.tabs(["Login", "Register"])

# --------------- LOGIN ---------------
with login_tab:
    st.subheader("Login")

    login_user = st.text_input("Username")
    login_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(login_user, login_pass):
            st.session_state.logged_in = True
            st.session_state.username = login_user
            st.success("Login successful!")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Invalid username or password")

# --------------- REGISTER ---------------
with register_tab:
    st.subheader("Register")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not new_user or not new_pass:
            st.warning("Please fill all fields")
        elif new_pass != confirm:
            st.error("Passwords do not match")
        elif get_user(new_user) is not None:
            st.error("Username already exists")
        else:
            create_user(new_user, new_pass)
            st.success("Account created! Please log in.")
