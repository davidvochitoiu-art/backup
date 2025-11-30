from Streamlit.app.data.schema import create_tables
from Streamlit.app.data.user_migration import migrate_users_from_txt
from Streamlit.app.data.load_csv import load_all_csv

from Streamlit.app.data.incidents import get_all_incidents
from Streamlit.app.data.datasets import get_all_datasets
from Streamlit.app.data.tickets import get_all_tickets


def main():
    print("=== WEEK 8: DATABASE SETUP & CRUD DEMO ===")

    create_tables()
    migrate_users_from_txt()
    load_all_csv()

    print("\n--- Cyber Incidents ---")
    print(get_all_incidents()[:115])

    print("\n--- Datasets ---")
    print(get_all_datasets()[:5])

    print("\n--- IT Tickets ---")
    print(get_all_tickets()[:150])

    print("\n✓ Week 8 complete.")


if __name__ == "__main__":
    main()
