from sqlalchemy import Column, Integer, String, ForeignKey, Time, Enum as SQLAlchemyEnum, Float
from sqlalchemy.orm import relationship
from .database import Base
import enum


# ------------------ ENUMS ------------------

class DayOfWeekEnum(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"


# ------------------ AUTH ------------------

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)


# ------------------ ACADEMIC CORE ------------------

class Department(Base):
    __tablename__ = "departments"
    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String, unique=True)

    subjects = relationship("Subject", back_populates="department")
    teachers = relationship("Teacher", back_populates="department")


class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String, nullable=False)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"))

    department = relationship("Department", back_populates="teachers")
    timetable_entries = relationship("Timetable", back_populates="teacher")


class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, unique=True)
    subject_name = Column(String, nullable=False)
    credits = Column(Float)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"))
    lectures_per_week = Column(Integer, default=4)

    department = relationship("Department", back_populates="subjects")
    timetable_entries = relationship("Timetable", back_populates="subject")


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    ts_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))


class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String, nullable=False)

    timetable_entries = relationship("Timetable", back_populates="room")


class TimeSlot(Base):
    __tablename__ = "time_slots"
    timeslot_id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(SQLAlchemyEnum(DayOfWeekEnum))
    period_no = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)


# ------------------ TIMETABLE ------------------

class Timetable(Base):
    __tablename__ = "timetable"
    timetable_id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(SQLAlchemyEnum(DayOfWeekEnum))
    period_no = Column(Integer)

    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))

    subject = relationship("Subject", back_populates="timetable_entries")
    teacher = relationship("Teacher", back_populates="timetable_entries")
    room = relationship("Room", back_populates="timetable_entries")
