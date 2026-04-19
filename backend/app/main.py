from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import (
    auth,
    patients,
    doctors,
    appointments,
    treatments,
    bills,
    rooms,
    medicines,
    analytics,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database is managed in database.py
    yield


from fastapi import APIRouter

app = FastAPI(
    title="SmartCare Hospital API",
    description="Core backend for SmartCare Hospital Management System",
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
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# Mount all routers
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(treatments.router)
api_router.include_router(bills.router)
api_router.include_router(rooms.router)
api_router.include_router(medicines.router)
api_router.include_router(analytics.router)

app.include_router(api_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "HMS API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
