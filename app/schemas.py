from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .models import DayOfWeekEnum

# ------------------ USER & AUTH ------------------

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ------------------ ACADEMIC ENTITIES ------------------

class Subject(BaseModel):
    subject_id: int
    subject_name: str
    dept_id: int

    class Config:
        from_attributes = True


class Teacher(BaseModel):
    teacher_id: int
    teacher_name: str

    class Config:
        from_attributes = True


class Room(BaseModel):
    room_id: int
    room_name: str

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    teacher_name: str
    dept_id: Optional[int] = None


# ------------------ TIMETABLE ------------------

class TimetableEntry(BaseModel):
    day_of_week: DayOfWeekEnum
    period_no: int
    subject: Subject
    teacher: Teacher
    room: Room

    class Config:
        from_attributes = True
