from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.medicine import MedicineCreate, MedicineUpdate, MedicineOut
from ..schemas.auth import UserOut
from ..auth.rbac import require_pharmacist

router = APIRouter(prefix="/medicines", tags=["Pharmacy"])


@router.get("/", response_model=list[MedicineOut])
def list_medicines(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM medicines ORDER BY medicine_id OFFSET %s LIMIT %s",
            (skip, limit),
        )
        medicines = cursor.fetchall()
        return [MedicineOut(**m) for m in medicines]
    finally:
        cursor.close()


@router.post("/", response_model=MedicineOut, status_code=201)
def create_medicine(
    body: MedicineCreate, db=Depends(get_db), _: UserOut = Depends(require_pharmacist)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    data = body.model_dump()
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ", ".join(["%s"] * len(columns))
    cols_str = ", ".join(columns)

    try:
        cursor.execute(
            f"INSERT INTO medicines ({cols_str}) VALUES ({placeholders}) RETURNING *",
            values,
        )
        med = cursor.fetchone()
        db.commit()
        return MedicineOut(**med)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(medicine_id: int, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM medicines WHERE medicine_id = %s LIMIT 1", (medicine_id,)
        )
        med = cursor.fetchone()
    finally:
        cursor.close()

    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    return MedicineOut(**med)


@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(
    medicine_id: int,
    body: MedicineUpdate,
    db=Depends(get_db),
    _: UserOut = Depends(require_pharmacist),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM medicines WHERE medicine_id = %s LIMIT 1", (medicine_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Medicine not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute(
                "SELECT * FROM medicines WHERE medicine_id = %s LIMIT 1", (medicine_id,)
            )
            return MedicineOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [medicine_id]

        cursor.execute(
            f"UPDATE medicines SET {set_clauses} WHERE medicine_id = %s RETURNING *",
            values,
        )
        med = cursor.fetchone()
        db.commit()
        return MedicineOut(**med)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(
    medicine_id: int, db=Depends(get_db), _: UserOut = Depends(require_pharmacist)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM medicines WHERE medicine_id = %s RETURNING medicine_id",
            (medicine_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Medicine not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
