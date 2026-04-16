from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base):
    __tablename__ = "APPOINTMENT"

    appointment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("PATIENT.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("DOCTOR.doctor_id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    reason = Column(String(300), nullable=True)
    notes = Column(Text, nullable=True)
    room_id = Column(Integer, ForeignKey("ROOM.room_id"), nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    room = relationship("Room", back_populates="appointments")
    bill = relationship("Bill", back_populates="appointment", uselist=False)
    treatment = relationship("Treatment", back_populates="appointment", uselist=False)
