from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.room import Room
from ..models.user import User
from ..schemas.room import RoomCreate, RoomUpdate, RoomOut
from ..auth.rbac import require_admin, require_any_staff

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomOut])
def list_rooms(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db),
               _: User = Depends(require_any_staff)):
    query = db.query(Room)
    if status:
        query = query.filter(Room.status == status)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=RoomOut, status_code=201)
def create_room(body: RoomCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    room = Room(**body.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db), _: User = Depends(require_any_staff)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomOut)
def update_room(room_id: int, body: RoomUpdate, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room
