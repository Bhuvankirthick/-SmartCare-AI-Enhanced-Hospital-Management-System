from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class MedicationItem(BaseModel):
    name: str
    dose: str
    duration: str
    instructions: Optional[str] = None


class TreatmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    description: Optional[str] = None
    medications: Optional[List[Any]] = None
    lab_results: Optional[str] = None
    cost: Optional[float] = 0.0


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentUpdate(BaseModel):
    diagnosis: Optional[str] = None
    description: Optional[str] = None
    medications: Optional[List[Any]] = None
    lab_results: Optional[str] = None
    cost: Optional[float] = None


class TreatmentOut(TreatmentBase):
    treatment_id: int
    treatment_date: datetime
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True
