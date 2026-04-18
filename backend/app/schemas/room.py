from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    room_type: str
    capacity: Optional[int] = 1
    cost_per_day: Optional[float] = 1000.0
    availability_status: Optional[str] = "Available"


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    cost_per_day: Optional[float] = None
    availability_status: Optional[str] = None


class RoomOut(RoomBase):
    room_id: int

    class Config:
        from_attributes = True
