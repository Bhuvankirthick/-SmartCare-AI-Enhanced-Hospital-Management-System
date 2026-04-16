from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Bill(Base):
    __tablename__ = "BILL"

    bill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("PATIENT.patient_id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("APPOINTMENT.appointment_id"), nullable=True)
    consultation_fee = Column(Float, default=0.0)
    treatment_cost = Column(Float, default=0.0)
    room_cost = Column(Float, default=0.0)
    medicine_cost = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_status = Column(Boolean, default=False)
    payment_method = Column(String(50), nullable=True)  # Cash, Card, Insurance
    bill_date = Column(DateTime, default=datetime.utcnow)
    items = Column(JSON, nullable=True)  # Detailed line items

    patient = relationship("Patient", back_populates="bills")
    appointment = relationship("Appointment", back_populates="bill")
