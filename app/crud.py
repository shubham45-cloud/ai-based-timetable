from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from app import models, schemas
from app.core.security import get_password_hash
from ortools.sat.python import cp_model


# ------------------ USER FUNCTIONS ------------------

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        role=user.role,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ------------------ DATA FETCHING FOR AI ENGINE ------------------

"""
crud_addition.py
────────────────────────────────────────────────────────────────────────
Paste these functions into your existing  app/crud.py
(they are the new calls the AI engine makes that didn't exist in v1)
────────────────────────────────────────────────────────────────────────
"""




# ── Already in your crud.py (shown here for reference) ───────────────────────

def get_all_teachers(db: Session):
    return db.query(models.Teacher).all()

def get_all_subjects(db: Session):
    return db.query(models.Subject).all()

def get_all_rooms(db: Session):
    return db.query(models.Room).all()

def get_all_time_slots(db: Session):
    return db.query(models.TimeSlot).all()

def get_all_teacher_subjects(db: Session):
    return db.query(models.TeacherSubject).all()

def clear_timetable(db: Session):
    db.query(models.Timetable).delete()
    db.flush()

def save_timetable_entry(db: Session, entry: dict, version_id: int):
    entry["version_id"] = version_id

    obj = models.Timetable(**entry)

    db.add(obj)
    db.flush()


# ── NEW – add this function ───────────────────────────────────────────────────

def get_combined_section_links(db: Session):
    """
    Returns all rows from the combined_sections table.
    Each row has:
        .combined_dept_id    – virtual combined department (e.g. CSE_4ABC)
        .constituent_dept_id – real section that is blocked when the
                               combined subject is scheduled
    """
    return db.query(models.CombinedSection).all()


# ── Convenience queries ───────────────────────────────────────────────────────

def get_timetable_by_section(db: Session, dept_id: int):
    """Return all timetable rows for a given section (dept_id)."""
    return (
        db.query(models.Timetable)
        .join(models.Subject, models.Timetable.subject_id == models.Subject.subject_id)
        .filter(models.Subject.dept_id == dept_id)
        .order_by(models.Timetable.day_of_week, models.Timetable.period_no)
        .all()
    )

def get_timetable_by_teacher(db: Session, teacher_id: int):
    """Return all timetable rows for a given teacher."""
    return (
        db.query(models.Timetable)
        .filter(models.Timetable.teacher_id == teacher_id)
        .order_by(models.Timetable.day_of_week, models.Timetable.period_no)
        .all()
    )

def get_full_timetable(db: Session):
    return (
        db.query(models.Timetable)
        .options(
            joinedload(models.Timetable.subject),
            joinedload(models.Timetable.teacher),
            joinedload(models.Timetable.room),
        )
        .order_by(
            models.Timetable.day_of_week,
            models.Timetable.period_no
        )
        .all()
    )
    
# ------------------ TIMETABLE VERSIONS ------------------

def create_timetable_version(
    db: Session,
    version_name: str,
    score: int = 0
):
    version = models.TimetableVersion(
        version_name=version_name,
        score=score
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


def get_timetable_versions(db: Session):
    return (
        db.query(models.TimetableVersion)
        .order_by(models.TimetableVersion.score.desc())
        .all()
    )


def select_timetable_version(
    db: Session,
    version_id: int
):
    db.query(models.TimetableVersion).update(
        {"is_selected": False}
    )

    version = (
        db.query(models.TimetableVersion)
        .filter(
            models.TimetableVersion.version_id == version_id
        )
        .first()
    )

    if version:
        version.is_selected = True
        db.commit()

    return version