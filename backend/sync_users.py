import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Add current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings
from app.auth.password import hash_password

def sync():
    print(f"Connecting to database at {settings.database_url.split('@')[-1]} for syncing users...")
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    default_password = hash_password("hospital123")
    
    try:
        # Sync Patients
        print("Syncing Patients...")
        cursor.execute("SELECT patient_id, name, email FROM patients")
        patients = cursor.fetchall()
        for p in patients:
            # Check if user exists
            cursor.execute("SELECT 1 FROM users WHERE role = 'patient' AND linked_id = %s", (p['patient_id'],))
            if not cursor.fetchone():
                username = p['name'].lower().replace(" ", "") + str(p['patient_id'])
                email = p['email'] if p['email'] else f"{username}@example.com"
                print(f"  Creating user for patient: {p['name']} ({username})")
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, linked_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                    (username, email, default_password, "patient", p['patient_id'])
                )

        # Sync Doctors
        print("\nSyncing Doctors...")
        cursor.execute("SELECT doctor_id, name, email FROM doctors")
        doctors = cursor.fetchall()
        for d in doctors:
            # Check if user exists
            cursor.execute("SELECT 1 FROM users WHERE role = 'doctor' AND linked_id = %s", (d['doctor_id'],))
            if not cursor.fetchone():
                username = d['name'].lower().replace(" ", "").replace(".", "") + str(d['doctor_id'])
                email = d['email'] if d['email'] else f"{username}@hospital.com"
                print(f"  Creating user for doctor: {d['name']} ({username})")
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, linked_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                    (username, email, default_password, "doctor", d['doctor_id'])
                )

        conn.commit()
        print("\n[OK] User synchronization complete!")
    except Exception as e:
        conn.rollback()
        print(f"❌ Sync failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sync()
