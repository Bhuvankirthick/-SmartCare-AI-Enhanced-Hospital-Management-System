from sqlalchemy import Column, Integer, String, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class RoomType(str, enum.Enum):
    GENERAL = "general"
    PRIVATE = "private"
    SEMI_PRIVATE = "semi_private"
    ICU = "icu"
    EMERGENCY = "emergency"


class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class Room(Base):
    __tablename__ = "ROOM"

    room_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(20), unique=True, nullable=False)
    room_type = Column(SAEnum(RoomType), default=RoomType.GENERAL)
    capacity = Column(Integer, default=1)
    current_occupancy = Column(Integer, default=0)
    daily_rate = Column(Float, default=1000.0)
    status = Column(SAEnum(RoomStatus), default=RoomStatus.AVAILABLE)
    floor = Column(Integer, nullable=True)

    appointments = relationship("Appointment", back_populates="room")
