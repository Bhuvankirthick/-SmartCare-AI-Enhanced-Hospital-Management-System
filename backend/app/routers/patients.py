from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.patient import PatientCreate, PatientUpdate, PatientOut
from ..schemas.auth import UserOut
from ..auth.password import hash_password
from ..auth.rbac import require_any_staff, get_current_user
from ..utils.notifications import send_notification

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=list[PatientOut])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    q: str = None,
    db=Depends(get_db),
    _: UserOut = Depends(require_any_staff),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        if q:
            cursor.execute(
                "SELECT * FROM patients WHERE name ILIKE %s ORDER BY patient_id OFFSET %s LIMIT %s",
                (f"%{q}%", skip, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM patients ORDER BY patient_id OFFSET %s LIMIT %s",
                (skip, limit),
            )
        return [PatientOut(**p) for p in cursor.fetchall()]
    finally:
        cursor.close()


@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(
    body: PatientCreate, db=Depends(get_db), _: UserOut = Depends(require_any_staff)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    # Extract patient data from request body
    patient_data = body.model_dump()
    patient_columns = list(patient_data.keys())
    patient_values = list(patient_data.values())
    patient_placeholders = ", ".join(["%s"] * len(patient_columns))
    patient_cols_str = ", ".join(patient_columns)
    try:
        # Insert patient and get full record including patient_id
        cursor.execute(
            f"INSERT INTO patients ({patient_cols_str}) VALUES ({patient_placeholders}) RETURNING *",
            patient_values,
        )
        patient = cursor.fetchone()
        # Create corresponding user entry linked to this patient
        hashed_pw = hash_password(body.password)
        user_columns = ["username", "email", "password", "role", "linked_id"]
        user_values = [body.username, body.email, hashed_pw, "patient", patient["patient_id"]]
        user_placeholders = ", ".join(["%s"] * len(user_columns))
        user_cols_str = ", ".join(user_columns)
        cursor.execute(
            f"INSERT INTO users ({user_cols_str}) VALUES ({user_placeholders}) RETURNING *",
            user_values,
        )
        # Commit transaction after both inserts
        db.commit()
        return PatientOut(**patient)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db=Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    if current_user.role == "patient" and current_user.linked_id != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")

    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM patients WHERE patient_id = %s LIMIT 1", (patient_id,)
        )
        patient = cursor.fetchone()
    finally:
        cursor.close()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientOut(**patient)


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    body: PatientUpdate,
    db=Depends(get_db),
    _: UserOut = Depends(require_any_staff),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM patients WHERE patient_id = %s LIMIT 1", (patient_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute(
                "SELECT * FROM patients WHERE patient_id = %s LIMIT 1", (patient_id,)
            )
            return PatientOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [patient_id]

        cursor.execute(
            f"UPDATE patients SET {set_clauses} WHERE patient_id = %s RETURNING *",
            values,
        )
        patient = cursor.fetchone()
        return PatientOut(**patient)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM patients WHERE patient_id = %s RETURNING patient_id",
            (patient_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
