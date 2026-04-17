from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
import random
from ..database import get_db
from ..schemas.auth import UserOut
from ..auth.rbac import require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats")
def get_stats(db=Depends(get_db), _: UserOut = Depends(require_admin)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_doctors = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT SUM(total_amount) FROM bills WHERE payment_status = 'Paid'"
        )
        total_revenue = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM bills WHERE payment_status = 'Pending'")
        pending_bills = cursor.fetchone()[0] or 0

        # Available beds: Rooms marked 'Available'
        cursor.execute(
            "SELECT SUM(capacity) FROM rooms WHERE availability_status = 'Available'"
        )
        available_beds = cursor.fetchone()[0] or 0

        # Low stock: Medicines with quantity < 50 (default threshold for now)
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock_quantity < 50")
        low_stock_count = cursor.fetchone()[0] or 0

        # Appointments by day (last 7 days)
        daily_appts = []
        for i in range(6, -1, -1):
            d = datetime.now() - timedelta(days=i)
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s",
                (d.date(),),
            )
            count = cursor.fetchone()[0] or 0
            daily_appts.append({"date": d.strftime("%b %d"), "count": count})

        # Revenue by month (last 6 months)
        monthly_revenue = []
        for i in range(5, -1, -1):
            d = datetime.now() - timedelta(days=i * 30)
            month_str = d.strftime("%Y-%m")
            cursor.execute(
                "SELECT SUM(total_amount) FROM bills WHERE TO_CHAR(bill_date, 'YYYY-MM') = %s AND payment_status = 'Paid'",
                (month_str,),
            )
            rev = cursor.fetchone()[0] or 0
            monthly_revenue.append(
                {"month": d.strftime("%b %Y"), "revenue": round(rev or 0, 2)}
            )

        # Appointment status breakdown
        status_breakdown = []
        statuses = ["Scheduled", "Completed", "Cancelled"]
        for status in statuses:
            cursor.execute(
                "SELECT COUNT(*) FROM appointments WHERE status = %s", (status,)
            )
            count = cursor.fetchone()[0] or 0
            status_breakdown.append({"status": status.lower(), "count": count})

        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "total_revenue": round(total_revenue or 0, 2),
            "pending_bills": pending_bills,
            "available_beds": int(available_beds),
            "low_stock_count": low_stock_count,
            "daily_appointments": daily_appts,
            "monthly_revenue": monthly_revenue,
            "status_breakdown": status_breakdown,
        }
    finally:
        cursor.close()


@router.get("/predictions")
def get_predictions(db=Depends(get_db), _: UserOut = Depends(require_admin)):
    """
    Return 7-day bed occupancy forecast.
    Fallback to statistical simulation since training data might be stale.
    """
    cursor = db.cursor()
    try:
        cursor.execute("SELECT SUM(capacity) FROM rooms")
        total_rooms = cursor.fetchone()[0] or 50

        # Occupied beds are rooms marked 'Occupied'
        cursor.execute(
            "SELECT SUM(capacity) FROM rooms WHERE availability_status = 'Occupied'"
        )
        current_occ = cursor.fetchone()[0] or 0
    finally:
        cursor.close()

    base_pct = (current_occ / total_rooms * 100) if total_rooms else 40

    predictions = []
    occ = base_pct
    for i in range(1, 8):
        d = datetime.now() + timedelta(days=i)
        day_factor = 1.15 if d.weekday() < 5 else 0.8
        occ = min(95, max(20, occ + random.uniform(-5, 7) * day_factor))
        predictions.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "day": d.strftime("%A"),
                "predicted_occupancy": round(occ, 1),
                "confidence_low": round(max(0, occ - 8), 1),
                "confidence_high": round(min(100, occ + 8), 1),
            }
        )
    return {"model": "statistical", "predictions": predictions}
