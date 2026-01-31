from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List  # <-- IMPORT THIS
from .. import crud, schemas
from ..database import get_db
from ..core import security, ai_engine

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users/create", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_admin: schemas.User = Depends(security.get_current_admin_user)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/timetable/generate", response_model=List[schemas.TimetableEntry])  # <-- CHANGE RESPONSE MODEL
def generate_timetable(db: Session = Depends(get_db), current_admin: schemas.User = Depends(security.get_current_admin_user)):
    """
    Triggers the AI engine to generate a new timetable and returns it.
    This is an admin-only endpoint.
    """
    result = ai_engine.generate_timetable_logic(db)
    if result["status"] == "error":
        raise HTTPException(status_code=409, detail=result["message"])
    
    # Fetch and return the newly created timetable
    new_timetable = crud.get_full_timetable(db)
    return new_timetable
@router.post("/reset-database")
def admin_reset_database(db: Session = Depends(get_db)):
    try:
        # Re-use the logic you just wrote
        tables = ["timetable", "teacher_subjects", "sections", "rooms", "teachers", "subjects"]
        db.execute(text("PRAGMA foreign_keys = OFF;"))
        for table in tables:
            db.execute(text(f"DELETE FROM {table};"))
            db.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{table}';"))
        db.execute(text("PRAGMA foreign_keys = ON;"))
        db.commit()
        return {"status": "success", "message": "Database wiped clean!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))