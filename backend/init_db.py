import psycopg2
from psycopg2 import sql
import sys
import os

# Add the current directory to sys.path so we can import from 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

def init_db():
    print(f"Connecting to database at {settings.database_url.split('@')[-1]}...")
    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # Drop existing tables to start fresh
    tables_to_drop = [
        "inventory_logs", "payments", "bills", "admissions", "prescription_medicines", 
        "prescriptions", "diagnoses", "appointments", "medicines", "rooms", 
        "doctor_departments", "departments", "doctors", "patients", "users"
    ]
    
    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    
    print("Cleaned up old tables.")

    commands = [
        # Authentication & Role Management
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE,
            password TEXT NOT NULL,
            role VARCHAR(20) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            linked_id INTEGER
        )
        """,
        # Core Entities
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dob DATE,
            gender VARCHAR(20),
            blood_group VARCHAR(10),
            contact VARCHAR(20),
            email VARCHAR(100),
            address TEXT,
            emergency_contact VARCHAR(20),
            insurance_id VARCHAR(50)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            contact VARCHAR(20),
            email VARCHAR(100),
            consultation_fee FLOAT DEFAULT 500.0,
            available BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS departments (
            department_id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS doctor_departments (
            doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
            department_id INTEGER REFERENCES departments(department_id) ON DELETE CASCADE,
            PRIMARY KEY (doctor_id, department_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS rooms (
            room_id SERIAL PRIMARY KEY,
            room_type VARCHAR(50) NOT NULL,
            capacity INTEGER DEFAULT 1,
            cost_per_day FLOAT DEFAULT 1000.0,
            availability_status VARCHAR(20) DEFAULT 'Available'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS medicines (
            medicine_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            price FLOAT DEFAULT 0.0,
            expiry_date DATE
        )
        """,
        # Clinical & Admin
        """
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
            doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
            appointment_date DATE NOT NULL,
            appointment_time TIME NOT NULL,
            status VARCHAR(20) DEFAULT 'Scheduled'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS diagnoses (
            diagnosis_id SERIAL PRIMARY KEY,
            appointment_id INTEGER REFERENCES appointments(appointment_id) ON DELETE CASCADE,
            diagnosis_details TEXT NOT NULL,
            notes TEXT,
            diagnosis_date DATE DEFAULT CURRENT_DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id SERIAL PRIMARY KEY,
            diagnosis_id INTEGER REFERENCES diagnoses(diagnosis_id) ON DELETE CASCADE,
            issued_date DATE DEFAULT CURRENT_DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS prescription_medicines (
            prescription_id INTEGER REFERENCES prescriptions(prescription_id) ON DELETE CASCADE,
            medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
            dosage VARCHAR(50),
            duration VARCHAR(50),
            quantity INTEGER,
            PRIMARY KEY (prescription_id, medicine_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS admissions (
            admission_id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
            room_id INTEGER REFERENCES rooms(room_id) ON DELETE SET NULL,
            admission_date DATE NOT NULL,
            discharge_date DATE
        )
        """,
        # Financials
        """
        CREATE TABLE IF NOT EXISTS bills (
            bill_id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
            admission_id INTEGER REFERENCES admissions(admission_id) ON DELETE SET NULL,
            total_amount FLOAT DEFAULT 0.0,
            bill_date DATE DEFAULT CURRENT_DATE,
            payment_status VARCHAR(20) DEFAULT 'Pending'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id SERIAL PRIMARY KEY,
            bill_id INTEGER REFERENCES bills(bill_id) ON DELETE CASCADE,
            amount_paid FLOAT NOT NULL,
            payment_date DATE DEFAULT CURRENT_DATE,
            payment_method VARCHAR(50)
        )
        """,
        # Inventory Log
        """
        CREATE TABLE IF NOT EXISTS inventory_logs (
            log_id SERIAL PRIMARY KEY,
            medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
            change_type VARCHAR(10), -- 'IN' or 'OUT'
            quantity INTEGER NOT NULL,
            log_date DATE DEFAULT CURRENT_DATE
        )
        """
    ]

    for command in commands:
        cursor.execute(command)

    print("New database schema initialized successfully!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
