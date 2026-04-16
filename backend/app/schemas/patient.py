from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class PatientBase(BaseModel):
    name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    name: Optional[str] = None


class PatientOut(PatientBase):
    patient_id: int

    class Config:
        from_attributes = True
