"""
HMS AI Data Pipeline
Pulls historical admission/appointment data from the database and exports a clean CSV for ML training.
Run from the ai/ directory: python data_pipeline.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pandas as pd
from datetime import datetime
from app.database import SessionLocal
from app.models.appointment import Appointment
from app.models.room import Room


def extract_data():
    db = SessionLocal()
    try:
        # Pull all appointments
        appts = db.query(Appointment).all()
        records = []
        for a in appts:
            records.append({
                "appointment_date": a.appointment_date,
                "day_of_week": a.appointment_date.weekday() if a.appointment_date else 0,
                "month": a.appointment_date.month if a.appointment_date else 1,
                "hour": a.appointment_date.hour if a.appointment_date else 9,
                "status": a.status.value,
                "doctor_id": a.doctor_id,
                "patient_id": a.patient_id,
            })

        df = pd.DataFrame(records)
        if df.empty:
            print("⚠ No appointment data found. Generating synthetic data for ML training.")
            df = _generate_synthetic_data()

        out_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
        df.to_csv(out_path, index=False)
        print(f"✅ Data pipeline complete. {len(df)} records saved to {out_path}")
        return df

    finally:
        db.close()


def _generate_synthetic_data():
    """Generate realistic synthetic admission data for MVP training."""
    import numpy as np
    np.random.seed(42)
    n = 500
    dates = pd.date_range(start="2023-01-01", periods=n, freq="6H")
    df = pd.DataFrame({
        "appointment_date": dates,
        "day_of_week": dates.dayofweek,
        "month": dates.month,
        "hour": dates.hour,
        "status": np.random.choice(["completed", "cancelled", "no_show"], n, p=[0.75, 0.15, 0.10]),
        "doctor_id": np.random.randint(1, 4, n),
        "patient_id": np.random.randint(1, 50, n),
        # Occupancy as target: realistic hospital bed occupancy %
        "bed_occupancy_pct": np.clip(
            50 + 15 * np.sin(2 * np.pi * dates.dayofweek / 7)
            + 10 * np.sin(2 * np.pi * dates.month / 12)
            + np.random.normal(0, 8, n),
            20, 98
        ).round(1),
    })
    return df


if __name__ == "__main__":
    extract_data()
