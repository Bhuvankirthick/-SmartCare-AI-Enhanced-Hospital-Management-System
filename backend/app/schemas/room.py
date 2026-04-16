from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    room_number: str
    room_type: Optional[str] = "general"
    capacity: Optional[int] = 1
    current_occupancy: Optional[int] = 0
    daily_rate: Optional[float] = 1000.0
    status: Optional[str] = "available"
    floor: Optional[int] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    daily_rate: Optional[float] = None
    status: Optional[str] = None
    floor: Optional[int] = None


class RoomOut(RoomBase):
    room_id: int

    class Config:
        from_attributes = True
