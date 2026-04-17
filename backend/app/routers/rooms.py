from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.room import RoomCreate, RoomUpdate, RoomOut
from ..schemas.auth import UserOut
from ..auth.rbac import require_admin

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomOut])
def list_rooms(status: str = None, skip: int = 0, limit: int = 100, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        if status:
            cursor.execute(
                "SELECT * FROM rooms WHERE availability_status = %s ORDER BY room_id OFFSET %s LIMIT %s",
                (status, skip, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM rooms ORDER BY room_id OFFSET %s LIMIT %s", (skip, limit)
            )
        return [RoomOut(**r) for r in cursor.fetchall()]
    finally:
        cursor.close()


@router.post("/", response_model=RoomOut, status_code=201)
def create_room(
    body: RoomCreate, db=Depends(get_db), _: UserOut = Depends(require_admin)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    data = body.model_dump()
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ", ".join(["%s"] * len(columns))
    cols_str = ", ".join(columns)

    try:
        cursor.execute(
            f"INSERT INTO rooms ({cols_str}) VALUES ({placeholders}) RETURNING *",
            values,
        )
        room = cursor.fetchone()
        db.commit()
        return RoomOut(**room)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s LIMIT 1", (room_id,))
        room = cursor.fetchone()
    finally:
        cursor.close()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomOut(**room)


@router.put("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: int,
    body: RoomUpdate,
    db=Depends(get_db),
    _: UserOut = Depends(require_admin),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s LIMIT 1", (room_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Room not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute("SELECT * FROM rooms WHERE room_id = %s LIMIT 1", (room_id,))
            return RoomOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [room_id]

        cursor.execute(
            f"UPDATE rooms SET {set_clauses} WHERE room_id = %s RETURNING *", values
        )
        room = cursor.fetchone()
        db.commit()
        return RoomOut(**room)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{room_id}", status_code=204)
def delete_room(room_id: int, db=Depends(get_db), _: UserOut = Depends(require_admin)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM rooms WHERE room_id = %s RETURNING room_id", (room_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Room not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
