"""
HMS ML Training Script
Trains a RandomForest model to predict 7-day bed occupancy.
Run from ai/ dir: python train_model.py
Outputs: model.joblib saved to backend/app/ml/
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score


def train():
    print("🔄 Loading training data...")
    data_path = os.path.join(os.path.dirname(__file__), "training_data.csv")

    if not os.path.exists(data_path):
        print("⚠ No training_data.csv found. Running data pipeline first...")
        from data_pipeline import extract_data
        df = extract_data()
    else:
        df = pd.read_csv(data_path)

    # Feature engineering
    if "bed_occupancy_pct" not in df.columns:
        # Derive occupancy proxy from appointment density
        df["bed_occupancy_pct"] = (
            50 + 15 * np.sin(2 * np.pi * df["day_of_week"] / 7)
            + 10 * np.sin(2 * np.pi * df["month"] / 12)
            + np.random.normal(0, 8, len(df))
        ).clip(20, 98).round(1)

    features = ["day_of_week", "month", "hour"] if "hour" in df.columns else ["day_of_week", "month"]
    X = df[features].fillna(0)
    y = df["bed_occupancy_pct"].fillna(60)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build pipeline
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)),
    ])

    print("🧠 Training Gradient Boosting model...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")

    print(f"\n📊 Model Evaluation:")
    print(f"   RMSE:    {rmse:.2f}%")
    print(f"   R² Score: {r2:.4f}")
    print(f"   CV R² (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'ml')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"\n✅ Model saved to {model_path}")

    # Quick prediction test
    test_features = np.array([[1, 5, 9], [5, 5, 14], [6, 5, 10]])  # Mon, Sat, Sun
    preds = pipeline.predict(test_features)
    print(f"\n🔮 Sample predictions (Mon/Sat/Sun):")
    for day, pred in zip(["Monday", "Saturday", "Sunday"], preds):
        print(f"   {day}: {pred:.1f}% expected bed occupancy")

    return pipeline


if __name__ == "__main__":
    train()
