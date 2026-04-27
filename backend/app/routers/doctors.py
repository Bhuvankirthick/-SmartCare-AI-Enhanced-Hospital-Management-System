from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.doctor import DoctorCreate, DoctorUpdate, DoctorOut
from ..schemas.auth import UserOut
from ..auth.rbac import require_admin, get_current_user
from ..auth.password import hash_password


router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorOut])
def list_doctors(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db),
    _: UserOut = Depends(get_current_user),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM doctors ORDER BY doctor_id OFFSET %s LIMIT %s", (skip, limit)
        )
        return [DoctorOut(**d) for d in cursor.fetchall()]
    finally:
        cursor.close()


@router.post("/", response_model=DoctorOut, status_code=201)
def create_doctor(
    body: DoctorCreate, db=Depends(get_db), _: UserOut = Depends(require_admin)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    data = body.model_dump()
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ", ".join(["%s"] * len(columns))
    cols_str = ", ".join(columns)

    try:
        cursor.execute(
            f"INSERT INTO doctors ({cols_str}) VALUES ({placeholders}) RETURNING *",
            values,
        )
        doctor = cursor.fetchone()
        
        # Create corresponding user entry linked to this doctor
        hashed_pw = hash_password(body.password)
        user_columns = ["username", "email", "password", "role", "linked_id"]
        user_values = [body.username, body.email, hashed_pw, "doctor", doctor["doctor_id"]]
        user_placeholders = ", ".join(["%s"] * len(user_columns))
        user_cols_str = ", ".join(user_columns)
        cursor.execute(
            f"INSERT INTO users ({user_cols_str}) VALUES ({user_placeholders})",
            user_values,
        )
        
        db.commit()
        return DoctorOut(**doctor)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int, db=Depends(get_db), _: UserOut = Depends(get_current_user)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM doctors WHERE doctor_id = %s LIMIT 1", (doctor_id,)
        )
        doctor = cursor.fetchone()
    finally:
        cursor.close()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return DoctorOut(**doctor)


@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(
    doctor_id: int,
    body: DoctorUpdate,
    db=Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    if current_user.role not in ("admin",) and current_user.linked_id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM doctors WHERE doctor_id = %s LIMIT 1", (doctor_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Doctor not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute(
                "SELECT * FROM doctors WHERE doctor_id = %s LIMIT 1", (doctor_id,)
            )
            return DoctorOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [doctor_id]

        cursor.execute(
            f"UPDATE doctors SET {set_clauses} WHERE doctor_id = %s RETURNING *", values
        )
        doctor = cursor.fetchone()
        db.commit()
        return DoctorOut(**doctor)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(
    doctor_id: int, db=Depends(get_db), _: UserOut = Depends(require_admin)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM doctors WHERE doctor_id = %s RETURNING doctor_id", (doctor_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Doctor not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
