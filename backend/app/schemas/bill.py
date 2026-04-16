from pydantic import BaseModel
from datetime import date
from typing import Optional


class BillBase(BaseModel):
    patient_id: int
    admission_id: Optional[int] = None
    total_amount: Optional[float] = 0.0
    payment_status: Optional[str] = "Pending"


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    payment_status: Optional[str] = None
    total_amount: Optional[float] = None


class BillOut(BillBase):
    bill_id: int
    bill_date: date
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True
