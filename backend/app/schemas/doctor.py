from pydantic import BaseModel
from typing import Optional


class DoctorBase(BaseModel):
    name: str
    specialization: str
    contact: Optional[str] = None
    email: Optional[str] = None
    consultation_fee: Optional[float] = 500.0
    available: Optional[bool] = True


class DoctorCreate(DoctorBase):
    username: str
    password: str


class DoctorUpdate(DoctorBase):
    name: Optional[str] = None
    specialization: Optional[str] = None


class DoctorOut(DoctorBase):
    doctor_id: int

    class Config:
        from_attributes = True
