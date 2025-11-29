import os
from app.data.db import get_connection

def migrate_users_from_txt(txt_path='DATA/users.txt'):
    if not os.path.exists(txt_path):
        print(f'users.txt not found at {txt_path}')
        return

    conn = get_connection()
    cursor = conn.cursor()

    with open(txt_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            username, password_hash = line.strip().split(',', 1)

            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (username, password_hash))

    conn.commit()
    conn.close()
    print('✓ Users migrated successfully from users.txt')
