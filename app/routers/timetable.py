from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_db
from ..core.security import get_current_user

router = APIRouter(
    prefix="/timetable",
    tags=["Timetable"],
)


# ------------------------
# 🎓 STUDENT: Branch Timetable
# ------------------------
@router.get("/branch/{dept_id}", response_model=List[schemas.TimetableEntry])
def get_timetable_for_branch(dept_id: int, db: Session = Depends(get_db)):
    """
    Returns timetable for a specific branch (department).
    """
    db_timetable = crud.get_full_timetable(db)

    branch_timetable = [
        entry for entry in db_timetable
        if entry.subject and entry.subject.dept_id == dept_id
    ]

    if not branch_timetable:
        raise HTTPException(
            status_code=404,
            detail="Timetable not found for this branch"
        )

    return branch_timetable


# ------------------------
# 👨‍🏫 TEACHER: My Timetable
# ------------------------
@router.get("/teacher/{teacher_name}", response_model=List[schemas.TimetableEntry])
def get_timetable_for_teacher(
    teacher_name: str,
    db: Session = Depends(get_db)
):
    teacher = db.query(models.Teacher).filter(
        models.Teacher.teacher_name == teacher_name
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    timetable = crud.get_full_timetable(db)

    teacher_timetable = [
        entry for entry in timetable
        if entry.teacher_id == teacher.teacher_id
    ]

    return teacher_timetable
