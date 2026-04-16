from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Any


class TreatmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    diagnosis_details: str


class TreatmentCreate(TreatmentBase):
    medications: Optional[List[Any]] = None


class TreatmentUpdate(BaseModel):
    diagnosis_details: Optional[str] = None


class TreatmentOut(TreatmentBase):
    diagnosis_id: int
    diagnosis_date: date
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True
