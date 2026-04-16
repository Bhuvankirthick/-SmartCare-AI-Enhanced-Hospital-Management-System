"""
HMS Seed Data Script
Run from backend/ directory: python seed_data.py
Creates demo users, patients, doctors, rooms, medicines, appointments, treatments, and bills.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from app.database import SessionLocal, create_all_tables
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment, AppointmentStatus
from app.models.treatment import Treatment
from app.models.bill import Bill
from app.models.room import Room, RoomType, RoomStatus
from app.models.medicine import Medicine
from app.auth.password import hash_password


def seed():
    create_all_tables()
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # ── DOCTORS ──
        doctors_data = [
            {"name": "Dr. Rajesh Kumar", "specialization": "Cardiology", "department": "Cardiology",
             "email": "rajesh@hms.com", "contact_number": "+91-9900001111", "consultation_fee": 800.0,
             "qualification": "MBBS, MD (Cardiology)", "available": True,
             "schedule": {"Mon": ["09:00","10:00","11:00"], "Tue": ["09:00","10:00","14:00"],
                          "Wed": ["09:00","11:00"], "Thu": ["10:00","11:00","15:00"], "Fri": ["09:00","10:00"]}},
            {"name": "Dr. Priya Sharma", "specialization": "Pediatrics", "department": "Pediatrics",
             "email": "priya@hms.com", "contact_number": "+91-9900002222", "consultation_fee": 600.0,
             "qualification": "MBBS, DCH", "available": True,
             "schedule": {"Mon": ["10:00","11:00","15:00"], "Tue": ["09:00","10:00"],
                          "Thu": ["09:00","14:00","15:00"], "Fri": ["10:00","11:00","16:00"]}},
            {"name": "Dr. Arun Mehta", "specialization": "Orthopedics", "department": "Surgery",
             "email": "arun@hms.com", "contact_number": "+91-9900003333", "consultation_fee": 700.0,
             "qualification": "MBBS, MS (Ortho)", "available": True,
             "schedule": {"Mon": ["09:00","10:00"], "Wed": ["09:00","10:00","11:00"],
                          "Fri": ["09:00","14:00","15:00"]}},
        ]
        doctors = [Doctor(**d) for d in doctors_data]
        db.add_all(doctors)
        db.flush()

        # ── PATIENTS ──
        patients_data = [
            {"name": "Ananya Patel", "gender": "Female", "blood_type": "A+",
             "contact_number": "+91-9800001111", "email": "ananya@gmail.com",
             "address": "12 MG Road, Bengaluru", "date_of_birth": datetime(1990, 5, 15).date(),
             "emergency_contact": "Ravi Patel: +91-9800001112"},
            {"name": "Vikram Singh", "gender": "Male", "blood_type": "O+",
             "contact_number": "+91-9800002222", "email": "vikram@gmail.com",
             "address": "45 Civil Lines, Jaipur", "date_of_birth": datetime(1978, 8, 22).date(),
             "emergency_contact": "Meena Singh: +91-9800002223"},
            {"name": "Sunita Rao", "gender": "Female", "blood_type": "B+",
             "contact_number": "+91-9800003333", "email": "sunita@gmail.com",
             "address": "7 Anna Nagar, Chennai", "date_of_birth": datetime(2001, 3, 10).date(),
             "emergency_contact": "Ramesh Rao: +91-9800003334"},
            {"name": "Kiran Joshi", "gender": "Male", "blood_type": "AB-",
             "contact_number": "+91-9800004444", "email": "kiran@gmail.com",
             "address": "89 Lal Bagh, Pune", "date_of_birth": datetime(1965, 11, 30).date(),
             "emergency_contact": "Kavita Joshi: +91-9800004445"},
        ]
        patients = [Patient(**p) for p in patients_data]
        db.add_all(patients)
        db.flush()

        # ── ROOMS ──
        rooms_data = [
            {"room_number": "G-101", "room_type": RoomType.GENERAL, "capacity": 4, "current_occupancy": 2,
             "daily_rate": 800.0, "status": RoomStatus.OCCUPIED, "floor": 1},
            {"room_number": "G-102", "room_type": RoomType.GENERAL, "capacity": 4, "current_occupancy": 0,
             "daily_rate": 800.0, "status": RoomStatus.AVAILABLE, "floor": 1},
            {"room_number": "P-201", "room_type": RoomType.PRIVATE, "capacity": 1, "current_occupancy": 1,
             "daily_rate": 2500.0, "status": RoomStatus.OCCUPIED, "floor": 2},
            {"room_number": "P-202", "room_type": RoomType.PRIVATE, "capacity": 1, "current_occupancy": 0,
             "daily_rate": 2500.0, "status": RoomStatus.AVAILABLE, "floor": 2},
            {"room_number": "ICU-01", "room_type": RoomType.ICU, "capacity": 2, "current_occupancy": 1,
             "daily_rate": 8000.0, "status": RoomStatus.OCCUPIED, "floor": 3},
            {"room_number": "SP-301", "room_type": RoomType.SEMI_PRIVATE, "capacity": 2, "current_occupancy": 0,
             "daily_rate": 1500.0, "status": RoomStatus.AVAILABLE, "floor": 3},
        ]
        rooms = [Room(**r) for r in rooms_data]
        db.add_all(rooms)
        db.flush()

        # ── MEDICINES ──
        medicines_data = [
            {"name": "Paracetamol 500mg", "category": "Analgesic", "stock_level": 500, "reorder_threshold": 100,
             "unit_price": 2.5, "supplier": "Sun Pharma", "unit": "tablets",
             "expiry_date": datetime(2027, 6, 30)},
            {"name": "Amoxicillin 250mg", "category": "Antibiotic", "stock_level": 15, "reorder_threshold": 50,
             "unit_price": 8.0, "supplier": "Cipla", "unit": "capsules",
             "expiry_date": datetime(2025, 12, 31)},
            {"name": "Metformin 500mg", "category": "Antidiabetic", "stock_level": 200, "reorder_threshold": 80,
             "unit_price": 3.0, "supplier": "Dr. Reddy's", "unit": "tablets",
             "expiry_date": datetime(2026, 9, 15)},
            {"name": "Atorvastatin 10mg", "category": "Lipid-lowering", "stock_level": 8, "reorder_threshold": 30,
             "unit_price": 12.5, "supplier": "Pfizer", "unit": "tablets",
             "expiry_date": datetime(2026, 3, 31)},
            {"name": "Omeprazole 20mg", "category": "Antacid", "stock_level": 180, "reorder_threshold": 60,
             "unit_price": 5.0, "supplier": "Lupin", "unit": "capsules",
             "expiry_date": datetime(2027, 1, 20)},
            {"name": "NS Saline 500ml", "category": "IV Fluid", "stock_level": 12, "reorder_threshold": 20,
             "unit_price": 45.0, "supplier": "Baxter", "unit": "bags",
             "expiry_date": datetime(2026, 8, 10)},
            {"name": "Insulin Regular 10ml", "category": "Hormone", "stock_level": 30, "reorder_threshold": 10,
             "unit_price": 180.0, "supplier": "Novo Nordisk", "unit": "vials",
             "expiry_date": datetime(2025, 11, 30)},
            {"name": "Ibuprofen 400mg", "category": "NSAID", "stock_level": 350, "reorder_threshold": 100,
             "unit_price": 4.0, "supplier": "Abbott", "unit": "tablets",
             "expiry_date": datetime(2027, 4, 15)},
        ]
        meds = [Medicine(**m) for m in medicines_data]
        db.add_all(meds)
        db.flush()

        # ── APPOINTMENTS ──
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        appt_data = [
            {"patient": patients[0], "doctor": doctors[0],
             "date": now - timedelta(days=3, hours=2), "status": AppointmentStatus.COMPLETED,
             "reason": "Chest pain evaluation"},
            {"patient": patients[1], "doctor": doctors[2],
             "date": now - timedelta(days=1, hours=1), "status": AppointmentStatus.COMPLETED,
             "reason": "Knee pain follow-up"},
            {"patient": patients[2], "doctor": doctors[1],
             "date": now + timedelta(hours=3), "status": AppointmentStatus.CONFIRMED,
             "reason": "Child vaccination"},
            {"patient": patients[3], "doctor": doctors[0],
             "date": now + timedelta(days=1, hours=4), "status": AppointmentStatus.SCHEDULED,
             "reason": "Hypertension management"},
            {"patient": patients[0], "doctor": doctors[1],
             "date": now + timedelta(days=2, hours=2), "status": AppointmentStatus.SCHEDULED,
             "reason": "Annual check-up"},
        ]
        appointments = []
        for ad in appt_data:
            a = Appointment(
                patient_id=ad["patient"].patient_id,
                doctor_id=ad["doctor"].doctor_id,
                appointment_date=ad["date"],
                status=ad["status"],
                reason=ad["reason"],
            )
            db.add(a)
            db.flush()
            appointments.append(a)

        # ── TREATMENTS ──
        treatment1 = Treatment(
            patient_id=patients[0].patient_id,
            doctor_id=doctors[0].doctor_id,
            appointment_id=appointments[0].appointment_id,
            diagnosis="Mild Hypertension Stage 1",
            description="Patient presents with BP 145/92. Started on antihypertensive therapy.",
            medications=[
                {"name": "Amlodipine 5mg", "dose": "1 tablet OD", "duration": "30 days",
                 "instructions": "Take in the morning"},
                {"name": "Atorvastatin 10mg", "dose": "1 tablet OD", "duration": "30 days",
                 "instructions": "Take at night"},
            ],
            lab_results="ECG: Normal sinus rhythm. Blood panel: Cholesterol 210 mg/dL. Creatinine: 1.1 mg/dL",
            cost=1200.0,
        )
        treatment2 = Treatment(
            patient_id=patients[1].patient_id,
            doctor_id=doctors[2].doctor_id,
            appointment_id=appointments[1].appointment_id,
            diagnosis="Osteoarthritis - Right Knee",
            description="Grade 2 OA on X-ray. Physiotherapy recommended. Pain management initiated.",
            medications=[
                {"name": "Ibuprofen 400mg", "dose": "1 tablet TDS", "duration": "7 days",
                 "instructions": "Take after meals"},
                {"name": "Calcium + D3", "dose": "1 tablet BD", "duration": "90 days",
                 "instructions": "Take with water"},
            ],
            lab_results="X-ray Right Knee: Mild joint space narrowing. Osteophytes present.",
            cost=900.0,
        )
        db.add_all([treatment1, treatment2])
        db.flush()

        # ── BILLS ──
        bill1 = Bill(
            patient_id=patients[0].patient_id,
            appointment_id=appointments[0].appointment_id,
            consultation_fee=800.0,
            treatment_cost=1200.0,
            room_cost=0.0,
            medicine_cost=150.0,
            paid_status=True,
            payment_method="Card",
            items=[
                {"desc": "Cardiology Consultation", "amount": 800.0},
                {"desc": "Treatment & Diagnosis", "amount": 1200.0},
                {"desc": "Medicines", "amount": 150.0},
            ],
        )
        bill1.total_amount = 800 + 1200 + 150
        bill2 = Bill(
            patient_id=patients[1].patient_id,
            appointment_id=appointments[1].appointment_id,
            consultation_fee=700.0,
            treatment_cost=900.0,
            room_cost=0.0,
            medicine_cost=80.0,
            paid_status=False,
            payment_method=None,
            items=[
                {"desc": "Orthopedics Consultation", "amount": 700.0},
                {"desc": "Treatment & X-Ray", "amount": 900.0},
                {"desc": "Medicines", "amount": 80.0},
            ],
        )
        bill2.total_amount = 700 + 900 + 80
        db.add_all([bill1, bill2])
        db.flush()

        # ── USERS ──
        users_data = [
            User(username="admin", email="admin@hms.com",
                 hashed_password=hash_password("admin123"), role=UserRole.ADMIN),
            User(username="dr.rajesh", email="rajesh@hms.com",
                 hashed_password=hash_password("doctor123"), role=UserRole.DOCTOR,
                 linked_id=doctors[0].doctor_id),
            User(username="dr.priya", email="priya_doc@hms.com",
                 hashed_password=hash_password("doctor123"), role=UserRole.DOCTOR,
                 linked_id=doctors[1].doctor_id),
            User(username="ananya.patient", email="ananya_p@gmail.com",
                 hashed_password=hash_password("patient123"), role=UserRole.PATIENT,
                 linked_id=patients[0].patient_id),
            User(username="receptionist", email="reception@hms.com",
                 hashed_password=hash_password("recept123"), role=UserRole.RECEPTIONIST),
            User(username="pharmacist", email="pharma@hms.com",
                 hashed_password=hash_password("pharma123"), role=UserRole.PHARMACIST),
        ]
        db.add_all(users_data)
        db.commit()

        print("[OK] Database seeded successfully!")
        print("\n[INFO] Demo Login Credentials:")
        print("  Admin:        admin / admin123")
        print("  Doctor:       dr.rajesh / doctor123")
        print("  Patient:      ananya.patient / patient123")
        print("  Receptionist: receptionist / recept123")
        print("  Pharmacist:   pharmacist / pharma123")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
