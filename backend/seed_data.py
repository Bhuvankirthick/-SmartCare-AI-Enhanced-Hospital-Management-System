import psycopg2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.auth.password import hash_password
from app.config import settings


def seed():
    print(
        f"Connecting to database at {settings.database_url.split('@')[-1]} for seeding..."
    )
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    try:
        # Check if users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded. Skipping.")
            return

        # Insert Admin User
        admin_pw = hash_password("admin123")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("admin", "admin@hms.com", admin_pw, "admin", True),
        )

        # Insert Doctor
        cursor.execute(
            """
            INSERT INTO doctors (name, specialization, contact, email, consultation_fee, available)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING doctor_id
            """,
            (
                "Dr. Rajesh Kumar",
                "Cardiology",
                "+91-9900001111",
                "rajesh@hms.com",
                800.0,
                True,
            ),
        )
        doc_id = cursor.fetchone()[0]

        doc_pw = hash_password("doctor123")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, is_active, linked_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            ("dr.rajesh", "rajesh@hms.com", doc_pw, "doctor", True, doc_id),
        )

        # Insert Patient
        cursor.execute(
            """
            INSERT INTO patients (name, gender, blood_group, contact, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING patient_id
            """,
            ("Ananya Patel", "Female", "A+", "+91-9800001111", "ananya@gmail.com"),
        )
        pat_id = cursor.fetchone()[0]

        pat_pw = hash_password("patient123")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, is_active, linked_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            ("ananya.patient", "ananya_p@gmail.com", pat_pw, "patient", True, pat_id),
        )

        # Insert Receptionist and Pharmacist
        rec_pw = hash_password("recept123")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("receptionist", "reception@hms.com", rec_pw, "receptionist", True),
        )
        pha_pw = hash_password("pharma123")
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("pharmacist", "pharma@hms.com", pha_pw, "pharmacist", True),
        )

        conn.commit()
        print("[OK] Database seeded successfully with psycopg2!")
        print("\n[INFO] Demo Login Credentials:")
        print("  Admin:        admin / admin123")
        print("  Doctor:       dr.rajesh / doctor123")
        print("  Patient:      ananya.patient / patient123")
        print("  Receptionist: receptionist / recept123")
        print("  Pharmacist:   pharmacist / pharma123")

    except Exception as e:
        conn.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed()
