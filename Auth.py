import bcrypt
import os

# ------------------------------
# CONFIGURATION
# ------------------------------
USER_DATA_FILE = "DATA/users.txt"

# ------------------------------
# PASSWORD HASHING FUNCTIONS
# ------------------------------

def hash_password(plain_text_password):
    # Encode password to bytes
    password_bytes = plain_text_password.encode("utf-8")

    # Generate salt
    salt = bcrypt.gensalt()

    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Decode back to string for storage
    return hashed.decode("utf-8")


def verify_password(plain_text_password, hashed_password):
    # Encode both to bytes
    password_bytes = plain_text_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Compare using bcrypt
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ------------------------------
# USER DATA HANDLING
# ------------------------------

def user_exists(username):
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            saved_username = line.strip().split(",")[0]
            if saved_username == username:
                return True

    return False


def register_user(username, password):
    # Check if user already exists
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False

    # Hash password
    hashed = hash_password(password)

    # Append to file
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed}\n")

    print(f"Success: User '{username}' registered successfully!")
    return True


def login_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users registered yet.")
        return False

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            saved_username, saved_hash = line.strip().split(",", 1)

            if saved_username == username:
                if verify_password(password, saved_hash):
                    print(f"Success: Welcome, {username}!")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False

    print("Error: Username not found.")
    return False


# ------------------------------
# INPUT VALIDATION
# ------------------------------

def validate_username(username):
    if not (3 <= len(username) <= 20):
        return False, "Username must be 3–20 characters."

    if not username.isalnum():
        return False, "Username must be alphanumeric."

    return True, ""


def validate_password(password):
    if not (6 <= len(password) <= 50):
        return False, "Password must be 6–50 characters."

    return True, ""


# ------------------------------
# MAIN MENU
# ------------------------------

def display_menu():
    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System - Week 7")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            is_valid, msg = validate_username(username)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            password = input("Enter a password: ").strip()

            is_valid, msg = validate_password(password)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            confirm = input("Confirm password: ").strip()
            if confirm != password:
                print("Error: Passwords do not match.")
                continue

            register_user(username, password)

        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            login_user(username, password)
            input("\nPress Enter to return to menu...")

        elif choice == '3':
            print("\nExiting system. Goodbye!")
            break

        else:
            print("Error: Invalid option. Choose 1–3.")


if __name__ == "__main__":
    main()
