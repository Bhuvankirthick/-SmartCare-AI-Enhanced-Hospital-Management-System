from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List


class BillBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    consultation_fee: Optional[float] = 0.0
    treatment_cost: Optional[float] = 0.0
    room_cost: Optional[float] = 0.0
    medicine_cost: Optional[float] = 0.0
    payment_method: Optional[str] = None
    items: Optional[Any] = None


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    paid_status: Optional[bool] = None
    payment_method: Optional[str] = None
    medicine_cost: Optional[float] = None


class BillOut(BillBase):
    bill_id: int
    total_amount: float
    paid_status: bool
    bill_date: datetime
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True
