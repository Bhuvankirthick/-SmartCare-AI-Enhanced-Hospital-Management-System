from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.treatment import TreatmentCreate, TreatmentUpdate, TreatmentOut
from ..schemas.auth import UserOut
from ..auth.rbac import get_current_user, require_doctor

router = APIRouter(prefix="/treatments", tags=["Treatments"])


@router.get("/", response_model=list[TreatmentOut])
def list_treatments(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    db=Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        base_query = """
            SELECT t.*, a.patient_id, a.doctor_id, d.name as doctor_name, p.name as patient_name
            FROM diagnoses t
            JOIN appointments a ON t.appointment_id = a.appointment_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            WHERE 1=1
        """
        params = []

        if current_user.role == "patient":
            base_query += " AND t.patient_id = %s"
            params.append(current_user.linked_id)
        elif patient_id:
            base_query += " AND t.patient_id = %s"
            params.append(patient_id)

        base_query += " ORDER BY t.diagnosis_date DESC OFFSET %s LIMIT %s"
        params.extend([skip, limit])

        cursor.execute(base_query, params)
        treatments = cursor.fetchall()
        return [TreatmentOut(**t) for t in treatments]
    finally:
        cursor.close()


@router.post("/", response_model=TreatmentOut, status_code=201)
def create_treatment(
    body: TreatmentCreate, db=Depends(get_db), _: UserOut = Depends(require_doctor)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            INSERT INTO diagnoses (patient_id, doctor_id, diagnosis_details)
            VALUES (%s, %s, %s)
            RETURNING diagnosis_id
            """,
            (body.patient_id, body.doctor_id, body.diagnosis_details),
        )
        new_id = cursor.fetchone()["diagnosis_id"]
        db.commit()

        cursor.execute(
            """
            SELECT t.*, d.name as doctor_name
            FROM diagnoses t
            LEFT JOIN doctors d ON t.doctor_id = d.doctor_id
            WHERE t.diagnosis_id = %s
        """,
            (new_id,),
        )
        return TreatmentOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{treatment_id}", response_model=TreatmentOut)
def get_treatment(
    treatment_id: int, db=Depends(get_db), _: UserOut = Depends(get_current_user)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            SELECT t.*, a.patient_id, a.doctor_id, d.name as doctor_name, p.name as patient_name
            FROM diagnoses t
            JOIN appointments a ON t.appointment_id = a.appointment_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            WHERE t.diagnosis_id = %s LIMIT 1
        """,
            (treatment_id,),
        )
        treatment = cursor.fetchone()
    finally:
        cursor.close()

    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return TreatmentOut(**treatment)


@router.put("/{treatment_id}", response_model=TreatmentOut)
def update_treatment(
    treatment_id: int,
    body: TreatmentUpdate,
    db=Depends(get_db),
    _: UserOut = Depends(require_doctor),
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM diagnoses WHERE diagnosis_id = %s LIMIT 1", (treatment_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Treatment not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute(
                """
                SELECT t.*, d.name as doctor_name
                FROM diagnoses t
                LEFT JOIN doctors d ON t.doctor_id = d.doctor_id
                WHERE t.diagnosis_id = %s LIMIT 1
            """,
                (treatment_id,),
            )
            return TreatmentOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [treatment_id]

        cursor.execute(
            f"UPDATE diagnoses SET {set_clauses} WHERE diagnosis_id = %s", values
        )
        db.commit()

        cursor.execute(
            """
            SELECT t.*, a.patient_id, a.doctor_id, d.name as doctor_name, p.name as patient_name
            FROM diagnoses t
            JOIN appointments a ON t.appointment_id = a.appointment_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            WHERE t.diagnosis_id = %s LIMIT 1
        """,
            (treatment_id,),
        )
        return TreatmentOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{treatment_id}", status_code=204)
def delete_treatment(
    treatment_id: int, db=Depends(get_db), _: UserOut = Depends(require_doctor)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM diagnoses WHERE diagnosis_id = %s RETURNING diagnosis_id",
            (treatment_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Diagnosis not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
