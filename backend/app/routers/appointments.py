from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models.appointment import Appointment, AppointmentStatus
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..models.user import User
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from ..auth.rbac import get_current_user, require_any_staff

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _check_conflict(db: Session, doctor_id: int, appointment_date: datetime, exclude_id: int = None):
    """Ensure no appointment overlaps within 30-minute window."""
    window_start = appointment_date - timedelta(minutes=29)
    window_end = appointment_date + timedelta(minutes=29)
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= window_start,
        Appointment.appointment_date <= window_end,
        Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
    )
    if exclude_id:
        query = query.filter(Appointment.appointment_id != exclude_id)
    return query.first()


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
    skip: int = 0, limit: int = 100,
    patient_id: int = None, doctor_id: int = None, date: str = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(Appointment)
    # Restrict patients to their own
    if current_user.role.value == "patient":
        query = query.filter(Appointment.patient_id == current_user.linked_id)
    elif current_user.role.value == "doctor":
        query = query.filter(Appointment.doctor_id == current_user.linked_id)
    else:
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(
                Appointment.appointment_date >= d,
                Appointment.appointment_date < d + timedelta(days=1)
            )
        except ValueError:
            pass

    appts = query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    result = []
    for a in appts:
        appt_dict = {
            "appointment_id": a.appointment_id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "appointment_date": a.appointment_date,
            "status": a.status.value,
            "reason": a.reason,
            "notes": a.notes,
            "room_id": a.room_id,
            "patient_name": a.patient.name if a.patient else None,
            "doctor_name": a.doctor.name if a.doctor else None,
        }
        result.append(appt_dict)
    return result


@router.post("/", response_model=AppointmentOut, status_code=201)
def create_appointment(body: AppointmentCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    # Scheduling conflict check
    conflict = _check_conflict(db, body.doctor_id, body.appointment_date)
    if conflict:
        raise HTTPException(status_code=409, detail="Doctor has a conflicting appointment at this time")

    appt = Appointment(**body.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    appt_dict = {
        "appointment_id": appt.appointment_id, "patient_id": appt.patient_id,
        "doctor_id": appt.doctor_id, "appointment_date": appt.appointment_date,
        "status": appt.status.value, "reason": appt.reason, "notes": appt.notes,
        "room_id": appt.room_id,
        "patient_name": appt.patient.name if appt.patient else None,
        "doctor_name": appt.doctor.name if appt.doctor else None,
    }
    return appt_dict


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    appt = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {
        "appointment_id": appt.appointment_id, "patient_id": appt.patient_id,
        "doctor_id": appt.doctor_id, "appointment_date": appt.appointment_date,
        "status": appt.status.value, "reason": appt.reason, "notes": appt.notes, "room_id": appt.room_id,
        "patient_name": appt.patient.name if appt.patient else None,
        "doctor_name": appt.doctor.name if appt.doctor else None,
    }


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, body: AppointmentUpdate, db: Session = Depends(get_db),
                       _: User = Depends(get_current_user)):
    appt = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if body.appointment_date and body.appointment_date != appt.appointment_date:
        conflict = _check_conflict(db, appt.doctor_id, body.appointment_date, exclude_id=appointment_id)
        if conflict:
            raise HTTPException(status_code=409, detail="Doctor has a conflicting appointment at this time")

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "status" and value:
            setattr(appt, field, AppointmentStatus(value))
        else:
            setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return {
        "appointment_id": appt.appointment_id, "patient_id": appt.patient_id,
        "doctor_id": appt.doctor_id, "appointment_date": appt.appointment_date,
        "status": appt.status.value, "reason": appt.reason, "notes": appt.notes, "room_id": appt.room_id,
        "patient_name": appt.patient.name if appt.patient else None,
        "doctor_name": appt.doctor.name if appt.doctor else None,
    }


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db),
                       _: User = Depends(require_any_staff)):
    appt = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.CANCELLED
    db.commit()
