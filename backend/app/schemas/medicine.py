from pydantic import BaseModel
from datetime import date
from typing import Optional


class MedicineBase(BaseModel):
    name: str
    stock_quantity: Optional[int] = 0
    price: Optional[float] = 0.0
    expiry_date: Optional[date] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[int] = None
    price: Optional[float] = None
    expiry_date: Optional[date] = None


class MedicineOut(MedicineBase):
    medicine_id: int

    class Config:
        from_attributes = True
