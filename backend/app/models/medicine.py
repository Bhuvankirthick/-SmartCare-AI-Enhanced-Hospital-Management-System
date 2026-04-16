from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from ..database import Base


class Medicine(Base):
    __tablename__ = "MEDICINE"

    medicine_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    stock_level = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=20)
    unit_price = Column(Float, default=0.0)
    supplier = Column(String(200), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    unit = Column(String(50), default="units")  # tablets, ml, strips, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
