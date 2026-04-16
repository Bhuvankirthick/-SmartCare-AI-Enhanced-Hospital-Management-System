from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Patient(Base):
    __tablename__ = "PATIENT"

    patient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_type = Column(String(10), nullable=True)
    contact_number = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True, unique=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    insurance_id = Column(String(80), nullable=True)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="patient", cascade="all, delete-orphan")
