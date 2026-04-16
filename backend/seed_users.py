import psycopg2
import sys
import os

# Add the current directory to sys.path so we can import from 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings
from app.auth.password import hash_password

def seed_users():
    print(f"Connecting to database at {settings.database_url.split('@')[-1]} for user seeding...")
    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    users = [
        # username, email, password, role, is_active, linked_id
        ("admin", "admin@hms.com", hash_password("admin123"), "admin", True, None),
        ("dr.ravi", "ravi@hospital.com", hash_password("doctor123"), "doctor", True, 1),
        ("arun.patient", "arun@gmail.com", hash_password("patient123"), "patient", True, 1),
        ("receptionist", "reception@hms.com", hash_password("recept123"), "receptionist", True, None),
        ("pharmacist", "pharma@hms.com", hash_password("pharma123"), "pharmacist", True, None),
    ]

    try:
        # Use "User" (table name from init_db.py)
        for u in users:
            cursor.execute(
                """
                INSERT INTO "User" (username, email, password, role, is_active, linked_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                u
            )
        print("Success: Users seeded successfully!")
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_users()
