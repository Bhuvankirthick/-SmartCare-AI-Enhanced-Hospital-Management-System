from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
import json
from ..database import get_db
from ..schemas.bill import BillCreate, BillUpdate, BillOut
from ..schemas.auth import UserOut
from ..auth.rbac import get_current_user, require_receptionist

router = APIRouter(prefix="/bills", tags=["Billing"])

@router.get("/", response_model=list[BillOut])
def list_bills(skip: int = 0, limit: int = 100, patient_id: int = None,
               db = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        base_query = """
            SELECT b.*, p.name as patient_name
            FROM bills b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE 1=1
        """
        params = []

        if current_user.role == "patient":
            base_query += " AND b.patient_id = %s"
            params.append(current_user.linked_id)
        elif patient_id:
            base_query += " AND b.patient_id = %s"
            params.append(patient_id)

        base_query += " ORDER BY b.bill_date DESC OFFSET %s LIMIT %s"
        params.extend([skip, limit])

        cursor.execute(base_query, params)
        bills = cursor.fetchall()
        return [BillOut(**b) for b in bills]
    finally:
        cursor.close()


@router.post("/", response_model=BillOut, status_code=201)
def create_bill(body: BillCreate, db = Depends(get_db), _: UserOut = Depends(require_receptionist)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    data = body.model_dump()
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ", ".join(["%s"] * len(columns))
    cols_str = ", ".join(columns)

    try:
        cursor.execute(
            f"INSERT INTO bills ({cols_str}) VALUES ({placeholders}) RETURNING bill_id", 
            values
        )
        new_id = cursor.fetchone()['bill_id']
        db.commit()

        cursor.execute("""
            SELECT b.*, p.name as patient_name
            FROM bills b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_id = %s
        """, (new_id,))
        return BillOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()

@router.get("/{bill_id}", response_model=BillOut)
def get_bill(bill_id: int, db = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT b.*, p.name as patient_name
            FROM bills b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_id = %s LIMIT 1
        """, (bill_id,))
        bill = cursor.fetchone()
    finally:
        cursor.close()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    if current_user.role == "patient" and bill['patient_id'] != current_user.linked_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return BillOut(**bill)


@router.put("/{bill_id}", response_model=BillOut)
def update_bill(bill_id: int, body: BillUpdate, db = Depends(get_db),
                _: UserOut = Depends(require_receptionist)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM bills WHERE bill_id = %s LIMIT 1", (bill_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Bill not found")

        data = body.model_dump(exclude_unset=True)
        if not data:
            cursor.execute("""
                SELECT b.*, p.name as patient_name
                FROM bills b
                LEFT JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.bill_id = %s LIMIT 1
            """, (bill_id,))
            return BillOut(**cursor.fetchone())

        set_clauses = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [bill_id]
        
        cursor.execute(
            f"UPDATE bills SET {set_clauses} WHERE bill_id = %s", 
            values
        )
        db.commit()

        cursor.execute("""
            SELECT b.*, p.name as patient_name
            FROM bills b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.bill_id = %s LIMIT 1
        """, (bill_id,))
        return BillOut(**cursor.fetchone())
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()

@router.delete("/{bill_id}", status_code=204)
def delete_bill(bill_id: int, db = Depends(get_db), _: UserOut = Depends(require_receptionist)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("DELETE FROM bills WHERE bill_id = %s RETURNING bill_id", (bill_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Bill not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
