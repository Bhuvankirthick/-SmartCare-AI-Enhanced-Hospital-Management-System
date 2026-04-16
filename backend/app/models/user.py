from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    RECEPTIONIST = "receptionist"
    PHARMACIST = "pharmacist"


class User(Base):
    __tablename__ = "USERS"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    linked_id = Column(Integer, nullable=True)  # FK to PATIENT/DOCTOR table based on role
