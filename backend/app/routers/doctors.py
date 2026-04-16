from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.doctor import Doctor
from ..models.user import User
from ..schemas.doctor import DoctorCreate, DoctorUpdate, DoctorOut
from ..auth.rbac import require_admin, get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorOut])
def list_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 _: User = Depends(get_current_user)):
    return db.query(Doctor).offset(skip).limit(limit).all()


@router.post("/", response_model=DoctorOut, status_code=201)
def create_doctor(body: DoctorCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    doctor = Doctor(**body.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, body: DoctorUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    # Admin or the doctor themselves can update
    if current_user.role.value not in ("admin",) and current_user.linked_id != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
