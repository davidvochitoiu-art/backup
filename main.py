import os
import sys
import hashlib

# --------------------------------------------------------------
# Correct imports that match your folder structure
# --------------------------------------------------------------
from Streamlit.app.services.database_manager import DatabaseManager
from Streamlit.app.services.ai_assistant import AIAssistant

from Streamlit.app.models.security_incident import SecurityIncident
from Streamlit.app.models.dataset import Dataset
from Streamlit.app.models.it_ticket import ITTicket


# ==============================================================
# Setup database absolute path (avoids operational errors)
# ==============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "Streamlit",
    "DATA",
    "intelligence_platform.db"
)

USERS_FILE = os.path.join(BASE_DIR, "users.txt")


# ==============================================================
# PASSWORD HASHING + AUTHENTICATION SYSTEM
# ==============================================================

def hash_password(password: str) -> str:
    """Simple SHA-256 hashing for user passwords."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user():
    print("\n--- Register New User ---")
    username = input("Choose a username: ").strip()
    password = input("Choose a password: ").strip()

    if not username or not password:
        print("ERROR: Username and password cannot be empty.")
        return False

    hashed = hash_password(password)

    # If users.txt doesn't exist, create it
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()

    # Check if user already exists
    with open(USERS_FILE, "r") as f:
        for line in f:
            stored_user, _ = line.strip().split("|")
            if stored_user == username:
                print("ERROR: Username already exists.")
                return False

    # Save new user
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}|{hashed}\n")

    print("Registration successful! You may now log in.")
    return True


def login_user():
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    hashed = hash_password(password)

    # No users yet?
    if not os.path.exists(USERS_FILE):
        print("No users registered yet. Please register first.")
        return False

    with open(USERS_FILE, "r") as f:
        for line in f:
            stored_user, stored_hash = line.strip().split("|")
            if stored_user == username and stored_hash == hashed:
                print(f"✔ Login successful! Welcome, {username}.")
                return True

    print("❌ Incorrect username or password.")
    return False


def auth_menu():
    """Simple terminal menu for login/register."""
    while True:
        print("\n==============================")
        print("      USER AUTHENTICATION     ")
        print("==============================")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            if login_user():
                return True
        elif choice == "2":
            register_user()
        elif choice == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Try again.")


# ==============================================================
# LOAD DATA FROM DATABASE (OOP models)
# ==============================================================

def load_data(db):
    # Load cyber incidents
    rows_inc = db.fetch_all(
        "SELECT incident_id, category, severity, status, description FROM cyber_incidents"
    )
    incidents = [SecurityIncident(*row) for row in rows_inc]

    # Load datasets
    rows_ds = db.fetch_all(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
    )
    datasets = [Dataset(*row) for row in rows_ds]

    # Load tickets
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

    return incidents, datasets, tickets


# ==============================================================
# BUILD INTELLIGENCE CONTEXT FOR THE AI MODEL
# ==============================================================

def build_context(incidents, datasets, tickets):
    context = "### SYSTEM INTELLIGENCE CONTEXT\n"

    # ----- INCIDENTS -----
    context += "\n## Cyber Incidents\n"
    if incidents:
        total = len(incidents)
        critical = sum(1 for i in incidents if i.get_severity().lower() == "critical")

        categories = [i.get_incident_type() for i in incidents]
        common_cat = max(set(categories), key=categories.count)

        context += (
            f"- Total: {total}\n"
            f"- Critical: {critical}\n"
            f"- Most common: {common_cat}\n"
        )
    else:
        context += "- No incidents.\n"

    # ----- DATASETS -----
    context += "\n## Datasets\n"
    if datasets:
        largest = max(datasets, key=lambda d: d.get_rows() or 0)

        context += (
            f"- Total datasets: {len(datasets)}\n"
            f"- Largest dataset: {largest.get_name()} ({largest.get_rows()} rows)\n"
        )
    else:
        context += "- No datasets.\n"

    # ----- TICKETS -----
    context += "\n## IT Tickets\n"
    if tickets:
        total = len(tickets)
        closed = sum(1 for t in tickets if t.get_status().lower() == "closed")

        staff = [t.get_assigned_to() for t in tickets if t.get_assigned_to()]
        top_worker = max(set(staff), key=staff.count) if staff else "None"

        context += (
            f"- Total tickets: {total}\n"
            f"- Closed: {closed}\n"
            f"- Most assigned staff: {top_worker}\n"
        )
    else:
        context += "- No tickets.\n"

    context += (
        "\n### Instructions\n"
        "If the user's question is NOT related to the system data, answer normally.\n"
    )

    return context


# ==============================================================
# TERMINAL CHAT ASSISTANT LOOP
# ==============================================================

def run_terminal_chat():
    print("\n---------------------------------------")
    print("🤖 AI Assistant — Terminal Mode")
    print("Type 'exit' to quit.")
    print("---------------------------------------\n")

    db = DatabaseManager(DB_PATH)
    ai = AIAssistant(model="phi3:mini")

    incidents, datasets, tickets = load_data(db)

    while True:
        user_input = input("You: ")

        if user_input.lower().strip() == "exit":
            print("\nAI: Goodbye! 👋")
            sys.exit()

        full_prompt = (
            build_context(incidents, datasets, tickets)
            + "\nUser question: "
            + user_input
        )

        response = ai.ask(full_prompt)

        print("\nAI:", response)
        print("\n---------------------------------------\n")


# ==============================================================
# MAIN ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    auth_menu()           # User must login/register first
    run_terminal_chat()   # Then they access the AI assistant
