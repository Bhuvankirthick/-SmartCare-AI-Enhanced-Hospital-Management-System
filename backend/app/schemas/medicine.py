from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MedicineBase(BaseModel):
    name: str
    category: Optional[str] = None
    stock_level: Optional[int] = 0
    reorder_threshold: Optional[int] = 20
    unit_price: Optional[float] = 0.0
    supplier: Optional[str] = None
    expiry_date: Optional[datetime] = None
    unit: Optional[str] = "units"


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    stock_level: Optional[int] = None
    reorder_threshold: Optional[int] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None
    expiry_date: Optional[datetime] = None
    unit: Optional[str] = None


class MedicineOut(MedicineBase):
    medicine_id: int
    is_low_stock: Optional[bool] = False

    class Config:
        from_attributes = True
