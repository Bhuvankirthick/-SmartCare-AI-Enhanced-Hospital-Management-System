import psycopg2
import sys
import os

# Add the current directory to sys.path so we can import from 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

def insert_data():
    print(f"Connecting to database at {settings.database_url.split('@')[-1]} for data insertion...")
    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = False # Use transactions
    cursor = conn.cursor()

    sql_commands = """
-- Clean up and reset sequences
TRUNCATE TABLE Patient, Doctor, Department, Room, Medicine, Appointment, Diagnosis, Prescription, Prescription_Medicine, Admission, Bill, Payment, Inventory_Log RESTART IDENTITY CASCADE;

-- =========================
-- PATIENT (10 rows)
-- =========================
INSERT INTO Patient (name, dob, gender, contact, blood_group, address) VALUES
('Arun Kumar','2002-05-10','Male','9876543210','B+','Chennai'),
('Bala Raj','2001-08-21','Male','9123456780','A+','Coimbatore'),
('Kiran Devi','2003-01-15','Female','9988776655','O+','Madurai'),
('Divya S','2000-12-11','Female','9001122334','AB+','Trichy'),
('Vignesh R','1999-03-09','Male','9002233445','B-','Salem'),
('Priya K','2002-09-18','Female','9003344556','A-','Erode'),
('Manoj P','2001-07-22','Male','9004455667','O-','Tirunelveli'),
('Sneha M','2003-02-14','Female','9005566778','B+','Vellore'),
('Ravi T','1998-11-30','Male','9006677889','A+','Chennai'),
('Anitha G','2000-06-05','Female','9007788990','O+','Madurai');

-- =========================
-- DOCTOR (5 rows)
-- =========================
INSERT INTO Doctor (name, specialization, contact, email) VALUES
('Dr. Ravi','Cardiology','9000000001','ravi@hospital.com'),
('Dr. Meena','Neurology','9000000002','meena@hospital.com'),
('Dr. Suresh','Orthopedics','9000000003','suresh@hospital.com'),
('Dr. Lakshmi','Dermatology','9000000004','lakshmi@hospital.com'),
('Dr. Kumar','General Medicine','9000000005','kumar@hospital.com');

-- =========================
-- DEPARTMENT (5 rows)
-- =========================
INSERT INTO Department (name) VALUES
('Cardiology'),('Neurology'),('Orthopedics'),('Dermatology'),('General Medicine');

-- =========================
-- DOCTOR_DEPARTMENT (5 rows)
-- =========================
INSERT INTO Doctor_Department (doctor_id, department_id) VALUES
(1,1),(2,2),(3,3),(4,4),(5,5);

-- =========================
-- ROOM (5 rows)
-- =========================
INSERT INTO Room (room_type, capacity, cost_per_day, availability_status) VALUES
('General',2,1000.00,'Available'),
('ICU',1,5000.00,'Occupied'),
('Private',1,3000.00,'Available'),
('Semi-Private',2,2000.00,'Available'),
('ICU',1,6000.00,'Occupied');

-- =========================
-- MEDICINE (6 rows)
-- =========================
INSERT INTO Medicine (name, stock_quantity, price, expiry_date) VALUES
('Paracetamol',200,5.50,'2027-12-31'),
('Aspirin',120,8.00,'2026-10-10'),
('Ibuprofen',150,6.75,'2027-05-20'),
('Amoxicillin',80,12.00,'2026-08-15'),
('Cetirizine',140,4.50,'2027-03-01'),
('Metformin',90,9.00,'2026-12-01');

-- =========================
-- APPOINTMENT (10 rows)
-- =========================
INSERT INTO Appointment (patient_id, doctor_id, appointment_date, appointment_time, status) VALUES
(1,1,'2026-04-20','10:30','Scheduled'),
(2,2,'2026-04-21','11:00','Completed'),
(3,3,'2026-04-21','12:00','Completed'),
(4,4,'2026-04-22','09:30','Scheduled'),
(5,5,'2026-04-22','10:00','Completed'),
(6,1,'2026-04-23','11:30','Scheduled'),
(7,2,'2026-04-23','12:30','Completed'),
(8,3,'2026-04-24','10:15','Scheduled'),
(9,4,'2026-04-24','11:45','Completed'),
(10,5,'2026-04-25','09:00','Scheduled');

-- =========================
-- DIAGNOSIS (10 rows)
-- =========================
INSERT INTO Diagnosis (appointment_id, diagnosis_details, notes, diagnosis_date) VALUES
(1,'Chest pain','ECG advised','2026-04-20'),
(2,'Migraine','Rest recommended','2026-04-21'),
(3,'Fracture','X-ray taken','2026-04-21'),
(4,'Skin allergy','Ointment advised','2026-04-22'),
(5,'Fever','Blood test','2026-04-22'),
(6,'Hypertension','Monitor BP','2026-04-23'),
(7,'Headache','Medication given','2026-04-23'),
(8,'Joint pain','Physiotherapy','2026-04-24'),
(9,'Rash','Allergy test','2026-04-24'),
(10,'Diabetes','Diet control','2026-04-25');

-- =========================
-- PRESCRIPTION (10 rows)
-- =========================
INSERT INTO Prescription (diagnosis_id, issued_date) VALUES
(1,'2026-04-20'),(2,'2026-04-21'),(3,'2026-04-21'),
(4,'2026-04-22'),(5,'2026-04-22'),(6,'2026-04-23'),
(7,'2026-04-23'),(8,'2026-04-24'),(9,'2026-04-24'),(10,'2026-04-25');

-- =========================
-- PRESCRIPTION_MEDICINE (12 rows)
-- =========================
INSERT INTO Prescription_Medicine (prescription_id, medicine_id, dosage, duration, quantity) VALUES
(1,1,'500mg','5 days',10),
(2,2,'100mg','3 days',6),
(3,3,'200mg','4 days',8),
(4,4,'250mg','5 days',10),
(5,5,'10mg','3 days',6),
(6,6,'500mg','7 days',14),
(7,1,'500mg','2 days',4),
(8,2,'100mg','2 days',4),
(9,3,'200mg','3 days',6),
(10,4,'250mg','4 days',8),
(5,1,'500mg','2 days',4),
(6,2,'100mg','2 days',4);

-- =========================
-- ADMISSION (6 rows)
-- =========================
INSERT INTO Admission (patient_id, room_id, admission_date, discharge_date) VALUES
(1,2,'2026-04-20','2026-04-25'),
(2,1,'2026-04-21','2026-04-23'),
(3,3,'2026-04-21','2026-04-24'),
(5,5,'2026-04-22','2026-04-26'),
(7,4,'2026-04-23','2026-04-27'),
(9,2,'2026-04-24','2026-04-28');

-- =========================
-- BILL (6 rows)
-- =========================
INSERT INTO Bill (patient_id, admission_id, total_amount, bill_date, payment_status) VALUES
(1,1,15000.00,'2026-04-25','Pending'),
(2,2,5000.00,'2026-04-23','Paid'),
(3,3,8000.00,'2026-04-24','Paid'),
(5,4,20000.00,'2026-04-26','Pending'),
(7,5,12000.00,'2026-04-27','Paid'),
(9,6,18000.00,'2026-04-28','Pending');

-- =========================
-- PAYMENT (4 rows)
-- =========================
INSERT INTO Payment (bill_id, amount_paid, payment_date, payment_method) VALUES
(2,5000.00,'2026-04-23','UPI'),
(3,8000.00,'2026-04-24','Cash'),
(5,12000.00,'2026-04-27','Card'),
(1,5000.00,'2026-04-25','UPI');  -- partial payment example

-- =========================
-- INVENTORY_LOG (8 rows)
-- =========================
INSERT INTO Inventory_Log (medicine_id, change_type, quantity, log_date) VALUES
(1,'OUT',10,'2026-04-20'),
(2,'OUT',6,'2026-04-21'),
(3,'OUT',8,'2026-04-21'),
(4,'OUT',10,'2026-04-22'),
(5,'OUT',6,'2026-04-22'),
(6,'OUT',14,'2026-04-23'),
(1,'IN',20,'2026-04-24'),
(2,'IN',15,'2026-04-25');
    """
    
    try:
        cursor.execute(sql_commands)
        conn.commit()
        print("Success: Data inserted successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error during insertion: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_data()
