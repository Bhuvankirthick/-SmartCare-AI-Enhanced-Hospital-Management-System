from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Treatment(Base):
    __tablename__ = "TREATMENT"

    treatment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("PATIENT.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("DOCTOR.doctor_id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("APPOINTMENT.appointment_id"), nullable=True)
    diagnosis = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    medications = Column(JSON, nullable=True)  # [{"name": "...", "dose": "...", "duration": "..."}]
    lab_results = Column(Text, nullable=True)
    cost = Column(Float, default=0.0)
    treatment_date = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="treatments")
    doctor = relationship("Doctor", back_populates="treatments")
    appointment = relationship("Appointment", back_populates="treatment")
