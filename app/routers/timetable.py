from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from .. import crud, schemas, models
from ..database import get_db
from ..core.security import get_current_user

router = APIRouter(
    prefix="/timetable",
    tags=["Timetable"],
)


# ─── DELETE must be defined BEFORE /teacher/{name} and /branch/{id} ─────────
# If it's defined after, FastAPI matches "delete" as the {teacher_name} param
# and returns 404 instead of hitting this handler.

@router.delete("/delete")
def delete_timetable(
    db: Session = Depends(get_db),
):
    """
    Wipes the entire timetable from the database.
    Both teacher and student screens will show empty after this.
    """
    try:
        db.execute(text("TRUNCATE TABLE timetable RESTART IDENTITY CASCADE;"))
        db.commit()
        return {"status": "success", "message": "Timetable deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ─── STUDENT: timetable by branch ────────────────────────────────────────────

@router.get("/branch/{dept_id}", response_model=List[schemas.TimetableEntry])
def get_timetable_for_branch(
    dept_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns timetable for a specific branch (department ID).
    Flutter student screen calls: GET /timetable/branch/1
    """
    all_entries = crud.get_full_timetable(db)

    branch_entries = [
        e for e in all_entries
        if e.subject and e.subject.dept_id == dept_id
    ]

    if not branch_entries:
        return []

    return branch_entries


# ─── TEACHER: timetable by name ──────────────────────────────────────────────

@router.get("/teacher/{teacher_name}", response_model=List[schemas.TimetableEntry])
def get_timetable_for_teacher(
    teacher_name: str,
    db: Session = Depends(get_db),
):
    """
    Returns timetable for a specific teacher by name.
    Flutter teacher screen calls: GET /timetable/teacher/Dr.%20Sharma
    """
    teacher = db.query(models.Teacher).filter(
        models.Teacher.teacher_name == teacher_name
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail=f"Teacher '{teacher_name}' not found in database."
        )

    all_entries = crud.get_full_timetable(db)

    teacher_entries = [
        e for e in all_entries
        if e.teacher_id == teacher.teacher_id
    ]

    # Return empty list (not 404) so Flutter shows "no classes" cleanly
    return teacher_entries