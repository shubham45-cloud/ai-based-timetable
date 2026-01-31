from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, admin, timetable

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Timetable Generator API",
    description="API for managing and generating academic timetables using AI.",
    version="1.0.0"
)

# --- CORRECTED CORS MIDDLEWARE ---
# Define the specific origins that are allowed to connect.
origins = [
    "http://127.0.0.1:3000",  # Your frontend's address
    "http://localhost:3000",
    "http://127.0.0.1:5500",  # <-- ADD THIS LINE
    "http://localhost:5500",    # Also add localhost for safety
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your dashboard to "talk" to the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------

# Include the API routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(timetable.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Timetable Generator API"}