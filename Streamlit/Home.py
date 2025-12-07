import streamlit as st
from app.services.database_manager import DatabaseManager
from app.services.auth_manager import AuthManager

st.set_page_config(page_title="Login / Register", layout="centered")

# -----------------------------------
# DATABASE + AUTH MANAGER
# -----------------------------------
db = DatabaseManager("DATA/intelligence_platform.db")   # fixed path
auth = AuthManager(db)

# -----------------------------------
# SESSION STATE INITIALISATION
# -----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# -----------------------------------
# ALREADY LOGGED IN? REDIRECT
# -----------------------------------
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")


# -----------------------------------
# PAGE UI
# -----------------------------------
st.title("🔐 Secure Login / Register")

login_tab, register_tab = st.tabs(["Login", "Register"])


# ==============================================================
#                           LOGIN TAB
# ==============================================================

with login_tab:
    st.subheader("Login to your account")

    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not login_username or not login_password:
            st.warning("Please fill in both fields.")
        else:
            user = auth.login_user(login_username, login_password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.get_username()
                st.success("Login successful! Redirecting...")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error("Invalid username or password.")


# ==============================================================
#                        REGISTER TAB
# ==============================================================

with register_tab:
    st.subheader("Create a new account")

    reg_username = st.text_input("New Username")
    reg_password = st.text_input("New Password", type="password")
    reg_confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not reg_username or not reg_password or not reg_confirm:
            st.warning("Please complete all fields.")
        elif reg_password != reg_confirm:
            st.error("Passwords do not match.")
        else:
            auth.register_user(reg_username, reg_password)
            st.success("Account created successfully! Please log in.")
