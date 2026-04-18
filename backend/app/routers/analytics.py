from fastapi import APIRouter, Depends
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.auth import UserOut
from ..auth.rbac import get_current_user

router = APIRouter(prefix="/analytics", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db=Depends(get_db), _: UserOut = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        # 1. Basic Counts
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_doctors = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()['count']

        # 2. Financials
        cursor.execute("SELECT SUM(total_amount) FROM bills WHERE payment_status = 'Paid'")
        total_revenue = cursor.fetchone()['sum'] or 0

        cursor.execute("SELECT COUNT(*) FROM bills WHERE payment_status = 'Pending'")
        pending_bills = cursor.fetchone()['count']

        # 3. Inventory & Rooms
        cursor.execute("SELECT COUNT(*) FROM rooms WHERE availability_status = 'Available'")
        available_beds = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock_quantity < 20")
        low_stock_count = cursor.fetchone()['count']

        # 4. Daily Appointments (Last 7 Days)
        cursor.execute("""
            SELECT TO_CHAR(appointment_date, 'DD Mon') as date, COUNT(*) as count
            FROM appointments
            WHERE appointment_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY appointment_date
            ORDER BY appointment_date
        """)
        daily_appts = cursor.fetchall()

        # 5. Status Breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM appointments
            GROUP BY status
        """)
        status_breakdown = cursor.fetchall()

        # 6. Monthly Revenue
        cursor.execute("""
            SELECT TO_CHAR(bill_date, 'Mon YYYY') as month, SUM(total_amount) as revenue
            FROM bills
            WHERE payment_status = 'Paid'
            GROUP BY TO_CHAR(bill_date, 'Mon YYYY'), DATE_TRUNC('month', bill_date)
            ORDER BY DATE_TRUNC('month', bill_date)
            LIMIT 6
        """)
        monthly_rev = cursor.fetchall()

        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "total_revenue": total_revenue,
            "pending_bills": pending_bills,
            "available_beds": available_beds,
            "low_stock_count": low_stock_count,
            "daily_appointments": daily_appts,
            "status_breakdown": status_breakdown,
            "monthly_revenue": monthly_rev
        }
    finally:
        cursor.close()

@router.get("/predictions")
def get_dummy_predictions():
    # Return dummy data since AI is removed
    return {
        "model": "statistical",
        "predictions": [
            {"day": "Mon", "date": "2026-04-20", "predicted_occupancy": 65, "confidence_low": 60, "confidence_high": 70},
            {"day": "Tue", "date": "2026-04-21", "predicted_occupancy": 70, "confidence_low": 65, "confidence_high": 75},
            {"day": "Wed", "date": "2026-04-22", "predicted_occupancy": 82, "confidence_low": 75, "confidence_high": 88},
            {"day": "Thu", "date": "2026-04-23", "predicted_occupancy": 78, "confidence_low": 72, "confidence_high": 84},
            {"day": "Fri", "date": "2026-04-24", "predicted_occupancy": 60, "confidence_low": 55, "confidence_high": 65},
            {"day": "Sat", "date": "2026-04-25", "predicted_occupancy": 55, "confidence_low": 50, "confidence_high": 60},
            {"day": "Sun", "date": "2026-04-26", "predicted_occupancy": 58, "confidence_low": 52, "confidence_high": 64},
        ]
    }
