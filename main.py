# main.py
from App.data.schema import create_tables
from App.data.user_migration import migrate_users_from_txt
from App.data.load_csv import load_all_csv

from App.data.users import get_all_users
from App.data.incidents import create_incident, get_all_incidents
from App.data.datasets import create_dataset, get_all_datasets
from App.data.tickets import create_ticket, get_all_tickets


def main():
    print("=== WEEK 8: DATABASE SETUP & CRUD DEMO ===")

    # 1. Create tables
    create_tables()

    # 2. Migrate users from users.txt
    migrate_users_from_txt()

    # 3. Load CSV data (if files are present)
    load_all_csv()

    # 4. Test CRUD: create sample records (optional)
    print("\n--- Creating sample records ---")
    create_incident("Test Incident", "High", status="open", date="2025-01-01")
    create_dataset("Test Dataset", "Lab", "Sample", 1234)
    create_ticket("Test Ticket", "Medium", status="open", created_date="2025-01-02")

    # 5. Read back some data
    print("\n--- Users ---")
    print(get_all_users())

    print("\n--- Incidents (first 5) ---")
    print(get_all_incidents()[:5])

    print("\n--- Datasets (first 5) ---")
    print(get_all_datasets()[:5])

    print("\n--- Tickets (first 5) ---")
    print(get_all_tickets()[:5])

    print("\n✓ Week 8 demo completed successfully.")


if __name__ == "__main__":
    main()
