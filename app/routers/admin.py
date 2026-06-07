from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from .. import crud, schemas
from ..database import get_db
from ..core import security, ai_engine

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ─── CREATE USER ─────────────────────────────────────────────────────────────

@router.post("/users/create", response_model=schemas.User)
def create_new_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.get_current_admin_user),
):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return crud.create_user(db=db, user=user)


# ─── GENERATE TIMETABLE ──────────────────────────────────────────────────────

@router.post("/timetable/generate")
def generate_timetable(
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.get_current_admin_user),
):
    """
    Runs the CP-SAT AI engine and writes a fresh timetable to the database.
    Admin only.
    """
    result = ai_engine.generate_timetable_logic(db)

    if result["status"] == "error":
        print(result)
        raise HTTPException(status_code=409, detail=result)

    return result   # {"status": "success", "message": "...", "entries": N}


# ─── RESET DATABASE ──────────────────────────────────────────────────────────

@router.post("/reset-database")
def reset_database(
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.get_current_admin_user),
):
    """
    Truncates all academic tables and resets ID sequences.
    WARNING: This wipes all data. Use only in dev/demo.
    """
    tables = [
        "timetable", "teacher_subjects", "time_slots",
        "sections", "rooms", "teachers", "subjects", "departments",
    ]
    try:
        table_string = ", ".join(tables)
        db.execute(text(f"TRUNCATE TABLE {table_string} RESTART IDENTITY CASCADE;"))
        db.commit()
        return {"status": "success", "message": "Database reset complete."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))