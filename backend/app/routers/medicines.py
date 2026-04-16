from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.medicine import Medicine
from ..models.user import User
from ..schemas.medicine import MedicineCreate, MedicineUpdate, MedicineOut
from ..auth.rbac import require_pharmacist, get_current_user

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("/", response_model=list[MedicineOut])
def list_medicines(skip: int = 0, limit: int = 200, low_stock: bool = False,
                   q: str = None, db: Session = Depends(get_db),
                   _: User = Depends(get_current_user)):
    query = db.query(Medicine)
    if low_stock:
        # Filter medicines where stock_level <= reorder_threshold
        query = query.filter(Medicine.stock_level <= Medicine.reorder_threshold)
    if q:
        query = query.filter(Medicine.name.ilike(f"%{q}%"))
    medicines = query.offset(skip).limit(limit).all()
    result = []
    for m in medicines:
        result.append({
            "medicine_id": m.medicine_id, "name": m.name, "category": m.category,
            "stock_level": m.stock_level, "reorder_threshold": m.reorder_threshold,
            "unit_price": m.unit_price, "supplier": m.supplier,
            "expiry_date": m.expiry_date, "unit": m.unit,
            "is_low_stock": m.stock_level <= m.reorder_threshold,
        })
    return result


@router.post("/", response_model=MedicineOut, status_code=201)
def create_medicine(body: MedicineCreate, db: Session = Depends(get_db),
                    _: User = Depends(require_pharmacist)):
    med = Medicine(**body.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return {**body.model_dump(), "medicine_id": med.medicine_id,
            "is_low_stock": med.stock_level <= med.reorder_threshold}


@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(medicine_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    m = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return {
        "medicine_id": m.medicine_id, "name": m.name, "category": m.category,
        "stock_level": m.stock_level, "reorder_threshold": m.reorder_threshold,
        "unit_price": m.unit_price, "supplier": m.supplier,
        "expiry_date": m.expiry_date, "unit": m.unit,
        "is_low_stock": m.stock_level <= m.reorder_threshold,
    }


@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(medicine_id: int, body: MedicineUpdate, db: Session = Depends(get_db),
                    _: User = Depends(require_pharmacist)):
    m = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    db.commit()
    db.refresh(m)
    return {
        "medicine_id": m.medicine_id, "name": m.name, "category": m.category,
        "stock_level": m.stock_level, "reorder_threshold": m.reorder_threshold,
        "unit_price": m.unit_price, "supplier": m.supplier,
        "expiry_date": m.expiry_date, "unit": m.unit,
        "is_low_stock": m.stock_level <= m.reorder_threshold,
    }


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db),
                    _: User = Depends(require_pharmacist)):
    m = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(m)
    db.commit()
