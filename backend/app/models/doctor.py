from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class Doctor(Base):
    __tablename__ = "DOCTOR"

    doctor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    specialization = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    contact_number = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True, unique=True)
    consultation_fee = Column(Float, default=500.0)
    schedule = Column(JSON, nullable=True)  # {"Mon": ["09:00","10:00",...], ...}
    available = Column(Boolean, default=True)
    qualification = Column(String(200), nullable=True)

    appointments = relationship("Appointment", back_populates="doctor")
    treatments = relationship("Treatment", back_populates="doctor")
