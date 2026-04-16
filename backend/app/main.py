from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import auth, patients, doctors, appointments, treatments, bills, rooms, medicines, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database is managed in database.py
    yield


app = FastAPI(
    title="Hospital Management System API",
    description="Comprehensive HMS with RBAC, EHR, Scheduling, Billing & AI Predictions",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(treatments.router)
app.include_router(bills.router)
app.include_router(rooms.router)
app.include_router(medicines.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "HMS API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
