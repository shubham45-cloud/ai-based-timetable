from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Time,
    Boolean,
    Float,
)

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.database import Base

import enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class DayOfWeekEnum(str, enum.Enum):
    MONDAY    = "MONDAY"
    TUESDAY   = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY  = "THURSDAY"
    FRIDAY    = "FRIDAY"
    SATURDAY  = "SATURDAY"


class RoomTypeEnum(str, enum.Enum):
    CLASSROOM = "CLASSROOM"   # regular 1-hour theory class
    LAB       = "LAB"         # 2-hour consecutive practical session


class SubjectTypeEnum(str, enum.Enum):
    THEORY = "THEORY"   # L + T  →  single periods in a classroom
    LAB    = "LAB"      # P      →  double (consecutive) periods in a lab


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    user_id  = Column(Integer, primary_key=True, index=True)
    name     = Column(String,  nullable=False)
    email    = Column(String,  unique=True, index=True, nullable=False)
    role     = Column(String,  nullable=False)
    password = Column(String,  nullable=False)


# ─────────────────────────────────────────────
# ACADEMIC CORE
# ─────────────────────────────────────────────

class Department(Base):
    """
    One row per section, e.g.
        CSE_4A, CSE_4B, CSE_4C  →  regular sections
        CSE_6A, CSE_6B
        CSE_8A                   →  online-only, skipped during scheduling
        CSE_4ABC                 →  virtual "combined" section (4A+4B+4C)
        CSE_6AB                  →  virtual "combined" section (6A+6B)
    """
    __tablename__ = "departments"
    dept_id   = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String,  unique=True)

    subjects          = relationship("Subject",         back_populates="department")
    teachers          = relationship("Teacher",         back_populates="department")
    # combined rows where THIS dept is the "combined" side
    combined_as_parent = relationship(
        "CombinedSection",
        foreign_keys="CombinedSection.combined_dept_id",
        back_populates="combined_dept"
    )


class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id   = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String,  nullable=False)
    dept_id      = Column(Integer, ForeignKey("departments.dept_id"))

    department       = relationship("Department",  back_populates="teachers")
    timetable_entries = relationship("Timetable", back_populates="teacher")


class Subject(Base):
    """
    One row per (subject × section) combination.

    lectures_per_week meaning:
        THEORY  →  total single-period slots per week  (= L + T)
        LAB     →  number of 2-hour sessions per week  (= P / 2)

    is_online = True  →  8th-sem / fully online subject, skipped by the AI engine.
    """
    __tablename__ = "subjects"
    subject_id       = Column(Integer, primary_key=True, index=True)
    subject_code     = Column(String,  unique=True)          # e.g. "BCSE0402_4A"
    subject_name     = Column(String,  nullable=False)
    credits          = Column(Float)
    dept_id          = Column(Integer, ForeignKey("departments.dept_id"))
    lectures_per_week = Column(Integer, default=3)
    subject_type     = Column(SQLAlchemyEnum(SubjectTypeEnum),
                              default=SubjectTypeEnum.THEORY)
    is_online        = Column(Boolean, default=False)

    department        = relationship("Department", back_populates="subjects")
    timetable_entries = relationship("Timetable",  back_populates="subject")


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    ts_id      = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))


class Room(Base):
    """
    room_type = CLASSROOM  →  assigned to THEORY subjects only
    room_type = LAB        →  assigned to LAB subjects only
    """
    __tablename__ = "rooms"
    room_id   = Column(Integer, primary_key=True, index=True)
    room_name = Column(String,  nullable=False)
    room_type = Column(SQLAlchemyEnum(RoomTypeEnum), default=RoomTypeEnum.CLASSROOM)

    timetable_entries = relationship("Timetable", back_populates="room")


class TimeSlot(Base):
    """
    Every row is a single 1-hour period.
    The AI engine automatically forms consecutive pairs for lab scheduling.
    """
    __tablename__ = "time_slots"
    timeslot_id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(SQLAlchemyEnum(DayOfWeekEnum))
    period_no   = Column(Integer)   # 1 … 8
    start_time  = Column(Time)
    end_time    = Column(Time)


class CombinedSection(Base):
    """
    Links a virtual "combined" department to its real constituent sections.

    Example rows
    ────────────────────────────────────────────────────
    combined_dept_id = 7 (CSE_4ABC)  │  constituent_dept_id = 1 (CSE_4A)
    combined_dept_id = 7 (CSE_4ABC)  │  constituent_dept_id = 2 (CSE_4B)
    combined_dept_id = 7 (CSE_4ABC)  │  constituent_dept_id = 3 (CSE_4C)
    combined_dept_id = 8 (CSE_6AB)   │  constituent_dept_id = 4 (CSE_6A)
    combined_dept_id = 8 (CSE_6AB)   │  constituent_dept_id = 5 (CSE_6B)
    ────────────────────────────────────────────────────
    When the AI engine places a combined subject at time T it simultaneously
    blocks all constituent sections from having any other class at time T.
    """
    __tablename__ = "combined_sections"
    id                  = Column(Integer, primary_key=True, index=True)
    combined_dept_id    = Column(Integer, ForeignKey("departments.dept_id"))
    constituent_dept_id = Column(Integer, ForeignKey("departments.dept_id"))

    combined_dept = relationship(
        "Department",
        foreign_keys=[combined_dept_id],
        back_populates="combined_as_parent"
    )


# ─────────────────────────────────────────────
# TIMETABLE
# ─────────────────────────────────────────────
class TimetableVersion(Base):
    __tablename__ = "timetable_versions"
    version_id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String, nullable=False)
    score = Column(Integer, default=0)
    is_selected = Column(Boolean, default=False)
    
class Timetable(Base):
    __tablename__ = "timetable"  
    timetable_id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        Integer,
        ForeignKey("timetable_versions.version_id")
    )
    day_of_week  = Column(SQLAlchemyEnum(DayOfWeekEnum))
    period_no    = Column(Integer)

    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    room_id    = Column(Integer, ForeignKey("rooms.room_id"))

    subject = relationship("Subject", back_populates="timetable_entries")
    teacher = relationship("Teacher", back_populates="timetable_entries")
    room    = relationship("Room",    back_populates="timetable_entries")