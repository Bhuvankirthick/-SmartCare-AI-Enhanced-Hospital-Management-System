from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.treatment import Treatment
from ..models.user import User
from ..schemas.treatment import TreatmentCreate, TreatmentUpdate, TreatmentOut
from ..auth.rbac import require_doctor, get_current_user

router = APIRouter(prefix="/treatments", tags=["Treatments"])


@router.get("/patient/{patient_id}", response_model=list[TreatmentOut])
def get_patient_treatments(patient_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    if current_user.role.value == "patient" and current_user.linked_id != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    treatments = db.query(Treatment).filter(Treatment.patient_id == patient_id).all()
    result = []
    for t in treatments:
        d = {
            "treatment_id": t.treatment_id, "patient_id": t.patient_id,
            "doctor_id": t.doctor_id, "appointment_id": t.appointment_id,
            "diagnosis": t.diagnosis, "description": t.description,
            "medications": t.medications, "lab_results": t.lab_results,
            "cost": t.cost, "treatment_date": t.treatment_date,
            "doctor_name": t.doctor.name if t.doctor else None,
        }
        result.append(d)
    return result


@router.get("/", response_model=list[TreatmentOut])
def list_treatments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    query = db.query(Treatment)
    if current_user.role.value == "doctor":
        query = query.filter(Treatment.doctor_id == current_user.linked_id)
    treatments = query.order_by(Treatment.treatment_date.desc()).offset(skip).limit(limit).all()
    result = []
    for t in treatments:
        d = {
            "treatment_id": t.treatment_id, "patient_id": t.patient_id,
            "doctor_id": t.doctor_id, "appointment_id": t.appointment_id,
            "diagnosis": t.diagnosis, "description": t.description,
            "medications": t.medications, "lab_results": t.lab_results,
            "cost": t.cost, "treatment_date": t.treatment_date,
            "doctor_name": t.doctor.name if t.doctor else None,
        }
        result.append(d)
    return result


@router.post("/", response_model=TreatmentOut, status_code=201)
def create_treatment(body: TreatmentCreate, db: Session = Depends(get_db),
                     _: User = Depends(require_doctor)):
    treatment = Treatment(**body.model_dump())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return {
        "treatment_id": treatment.treatment_id, "patient_id": treatment.patient_id,
        "doctor_id": treatment.doctor_id, "appointment_id": treatment.appointment_id,
        "diagnosis": treatment.diagnosis, "description": treatment.description,
        "medications": treatment.medications, "lab_results": treatment.lab_results,
        "cost": treatment.cost, "treatment_date": treatment.treatment_date,
        "doctor_name": treatment.doctor.name if treatment.doctor else None,
    }


@router.put("/{treatment_id}", response_model=TreatmentOut)
def update_treatment(treatment_id: int, body: TreatmentUpdate, db: Session = Depends(get_db),
                     _: User = Depends(require_doctor)):
    treatment = db.query(Treatment).filter(Treatment.treatment_id == treatment_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(treatment, field, value)
    db.commit()
    db.refresh(treatment)
    return {
        "treatment_id": treatment.treatment_id, "patient_id": treatment.patient_id,
        "doctor_id": treatment.doctor_id, "appointment_id": treatment.appointment_id,
        "diagnosis": treatment.diagnosis, "description": treatment.description,
        "medications": treatment.medications, "lab_results": treatment.lab_results,
        "cost": treatment.cost, "treatment_date": treatment.treatment_date,
        "doctor_name": treatment.doctor.name if treatment.doctor else None,
    }
