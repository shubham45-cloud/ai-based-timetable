from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from . import models, schemas
from .core.security import get_password_hash


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

def get_all_teachers(db: Session):
    return db.query(models.Teacher).all()


def get_all_subjects(db: Session):
    return db.query(models.Subject).all()


def get_all_rooms(db: Session):
    return db.query(models.Room).all()


def get_all_teacher_subjects(db: Session):
    return db.query(models.TeacherSubject).all()


def get_all_time_slots(db: Session):
    return (
        db.query(models.TimeSlot)
        .order_by(models.TimeSlot.day_of_week, models.TimeSlot.period_no)
        .all()
    )


# ------------------ TIMETABLE MANAGEMENT ------------------

def clear_timetable(db: Session):
    """
    Clears timetable completely.
    Used before regenerating timetable (demo-friendly).
    """
    try:
        db.execute(text("TRUNCATE TABLE timetable RESTART IDENTITY CASCADE;"))
        db.commit()
        print("✅ Timetable cleared successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Truncate failed, falling back to delete: {e}")
        db.query(models.Timetable).delete(synchronize_session=False)
        db.commit()


def save_timetable_entry(db: Session, entry: dict):
    """
    Saves a single timetable slot.
    Commit should be done outside (bulk insert).
    """
    db_entry = models.Timetable(**entry)
    db.add(db_entry)


def get_full_timetable(db: Session):
    """
    Fetches full timetable with related names.
    BRANCH-ONLY (no sections).
    """
    return (
        db.query(models.Timetable)
        .options(
            joinedload(models.Timetable.subject),
            joinedload(models.Timetable.teacher),
            joinedload(models.Timetable.room),
        )
        .order_by(
            models.Timetable.day_of_week,
            models.Timetable.period_no,
        )
        .all()
    )
