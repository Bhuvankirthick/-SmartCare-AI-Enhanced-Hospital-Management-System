from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.bill import Bill
from ..models.appointment import Appointment
from ..models.user import User
from ..schemas.bill import BillCreate, BillUpdate, BillOut
from ..auth.rbac import require_admin, get_current_user

router = APIRouter(prefix="/bills", tags=["Billing"])


def _compute_total(b: Bill) -> float:
    return (b.consultation_fee or 0) + (b.treatment_cost or 0) + (b.room_cost or 0) + (b.medicine_cost or 0)


@router.get("/", response_model=list[BillOut])
def list_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    query = db.query(Bill)
    if current_user.role.value == "patient":
        query = query.filter(Bill.patient_id == current_user.linked_id)
    bills = query.order_by(Bill.bill_date.desc()).offset(skip).limit(limit).all()
    result = []
    for b in bills:
        result.append({
            "bill_id": b.bill_id, "patient_id": b.patient_id, "appointment_id": b.appointment_id,
            "consultation_fee": b.consultation_fee, "treatment_cost": b.treatment_cost,
            "room_cost": b.room_cost, "medicine_cost": b.medicine_cost,
            "total_amount": b.total_amount, "paid_status": b.paid_status,
            "payment_method": b.payment_method, "bill_date": b.bill_date, "items": b.items,
            "patient_name": b.patient.name if b.patient else None,
        })
    return result


@router.get("/patient/{patient_id}", response_model=list[BillOut])
def get_patient_bills(patient_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    if current_user.role.value == "patient" and current_user.linked_id != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    bills = db.query(Bill).filter(Bill.patient_id == patient_id).all()
    return [{
        "bill_id": b.bill_id, "patient_id": b.patient_id, "appointment_id": b.appointment_id,
        "consultation_fee": b.consultation_fee, "treatment_cost": b.treatment_cost,
        "room_cost": b.room_cost, "medicine_cost": b.medicine_cost,
        "total_amount": b.total_amount, "paid_status": b.paid_status,
        "payment_method": b.payment_method, "bill_date": b.bill_date, "items": b.items,
        "patient_name": b.patient.name if b.patient else None,
    } for b in bills]


@router.post("/", response_model=BillOut, status_code=201)
def create_bill(body: BillCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    # Auto-pull consultation fee from appointment's doctor if not provided
    if body.appointment_id and not body.consultation_fee:
        appt = db.query(Appointment).filter(Appointment.appointment_id == body.appointment_id).first()
        if appt and appt.doctor:
            body = body.model_copy(update={"consultation_fee": appt.doctor.consultation_fee})

    bill = Bill(**body.model_dump())
    bill.total_amount = _compute_total(bill)
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return {
        "bill_id": bill.bill_id, "patient_id": bill.patient_id, "appointment_id": bill.appointment_id,
        "consultation_fee": bill.consultation_fee, "treatment_cost": bill.treatment_cost,
        "room_cost": bill.room_cost, "medicine_cost": bill.medicine_cost,
        "total_amount": bill.total_amount, "paid_status": bill.paid_status,
        "payment_method": bill.payment_method, "bill_date": bill.bill_date, "items": bill.items,
        "patient_name": bill.patient.name if bill.patient else None,
    }


@router.put("/{bill_id}/pay", response_model=BillOut)
def mark_paid(bill_id: int, body: BillUpdate, db: Session = Depends(get_db),
              _: User = Depends(require_admin)):
    bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(bill, field, value)
    bill.total_amount = _compute_total(bill)
    db.commit()
    db.refresh(bill)
    return {
        "bill_id": bill.bill_id, "patient_id": bill.patient_id, "appointment_id": bill.appointment_id,
        "consultation_fee": bill.consultation_fee, "treatment_cost": bill.treatment_cost,
        "room_cost": bill.room_cost, "medicine_cost": bill.medicine_cost,
        "total_amount": bill.total_amount, "paid_status": bill.paid_status,
        "payment_method": bill.payment_method, "bill_date": bill.bill_date, "items": bill.items,
        "patient_name": bill.patient.name if bill.patient else None,
    }
