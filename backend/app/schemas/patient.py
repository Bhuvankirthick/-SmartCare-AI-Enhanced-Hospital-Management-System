from pydantic import BaseModel
from datetime import date
from typing import Optional


class PatientBase(BaseModel):
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientCreate(PatientBase):
    username: str
    password: str


class PatientUpdate(PatientBase):
    name: Optional[str] = None


class PatientOut(PatientBase):
    patient_id: int

    class Config:
        from_attributes = True
