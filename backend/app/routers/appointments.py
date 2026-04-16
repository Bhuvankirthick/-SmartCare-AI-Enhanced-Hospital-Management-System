from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, time, timedelta
from ..database import get_db
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from ..schemas.auth import UserOut
from ..auth.rbac import get_current_user, require_any_staff

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _check_conflict(cursor, doctor_id: int, appointment_date: date, appointment_time: time, exclude_id: int = None):
    """Ensure no appointment overlaps at the exact same time."""
    query = """
        SELECT appointment_id FROM appointments
        WHERE doctor_id = %s
        AND appointment_date = %s
        AND appointment_time = %s
        AND status NOT IN ('cancelled', 'no_show')
    """
    params = [doctor_id, appointment_date, appointment_time]
    
    if exclude_id:
        query += " AND appointment_id != %s"
        params.append(exclude_id)
        
    cursor.execute(query, params)
    return cursor.fetchone()


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
    skip: int = 0, limit: int = 100,
    patient_id: int = None, doctor_id: int = None, date_str: str = None,
    db = Depends(get_db), current_user: UserOut = Depends(get_current_user)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        base_query = """
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE 1=1
        """
        params = []
        
        if current_user.role == "patient":
            base_query += " AND a.patient_id = %s"
            params.append(current_user.linked_id)
        elif current_user.role == "doctor":
            base_query += " AND a.doctor_id = %s"
            params.append(current_user.linked_id)
        else:
            if patient_id:
                base_query += " AND a.patient_id = %s"
                params.append(patient_id)
            if doctor_id:
                base_query += " AND a.doctor_id = %s"
                params.append(doctor_id)

        if date_str:
            try:
                base_query += " AND a.appointment_date = %s"
                params.append(date_str)
            except ValueError:
                pass
                
        base_query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC OFFSET %s LIMIT %s"
        params.extend([skip, limit])
        
        cursor.execute(base_query, params)
        appts = cursor.fetchall()
        return [AppointmentOut(**a) for a in appts]
    finally:
        cursor.close()


@router.post("/", response_model=AppointmentOut, status_code=201)
def create_appointment(body: AppointmentCreate, db = Depends(get_db),
                       current_user: UserOut = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        # Scheduling conflict check
        conflict = _check_conflict(cursor, body.doctor_id, body.appointment_date, body.appointment_time)
        if conflict:
            raise HTTPException(status_code=409, detail="Doctor has a conflicting appointment at this time")

        data = body.model_dump()
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["%s"] * len(columns))
        cols_str = ", ".join(columns)

        cursor.execute(
            f"INSERT INTO appointments ({cols_str}) VALUES ({placeholders}) RETURNING appointment_id", 
            values
        )
        new_id = cursor.fetchone()['appointment_id']
        db.commit()
        
        # Fetch complete object with names
        cursor.execute("""
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = %s
        """, (new_id,))
        return AppointmentOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db = Depends(get_db), _: UserOut = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = %s LIMIT 1
        """, (appointment_id,))
        appt = cursor.fetchone()
    finally:
        cursor.close()

    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    return AppointmentOut(**appt)


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, body: AppointmentUpdate, db = Depends(get_db),
                       _: UserOut = Depends(get_current_user)):
                       
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM appointments WHERE appointment_id = %s LIMIT 1", (appointment_id,))
        appt = cursor.fetchone()
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Conflict check if date or time changed
        new_date = body.appointment_date or appt['appointment_date']
        new_time = body.appointment_time or appt['appointment_time']
        if (body.appointment_date and body.appointment_date != appt['appointment_date']) or \
           (body.appointment_time and body.appointment_time != appt['appointment_time']):
            conflict = _check_conflict(cursor, appt['doctor_id'], new_date, new_time, exclude_id=appointment_id)
            if conflict:
                raise HTTPException(status_code=409, detail="Doctor has a conflicting appointment at this time")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute("""
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_id = %s LIMIT 1
            """, (appointment_id,))
            return AppointmentOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [appointment_id]
        
        cursor.execute(
            f"UPDATE appointments SET {set_clauses} WHERE appointment_id = %s", 
            values
        )
        db.commit()
        
        # Fetch updated with names
        cursor.execute("""
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = %s LIMIT 1
        """, (appointment_id,))
        
        return AppointmentOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(appointment_id: int, db = Depends(get_db),
                       _: UserOut = Depends(require_any_staff)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("UPDATE appointments SET status = 'cancelled' WHERE appointment_id = %s RETURNING appointment_id", (appointment_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Appointment not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
