import sys
import os

# Maintain the path logic to allow importing from the app directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_resources():
    db = SessionLocal()
    try:
        print("🌱 Seeding FULL college-level timetable data...")

        # -------------------------------------------------
        # 0️⃣ ADMIN USER
        # -------------------------------------------------
        admin_email = "admin@example.com"
        admin = db.query(models.User).filter_by(email=admin_email).first()
        
        if not admin:
            print("Creating admin user...")
            admin = models.User(
                name="Admin",
                email=admin_email,
                role="admin",
                password=hash_password("admin123")
            )
            db.add(admin)
            db.flush()  # Ensure admin is staged before proceeding

        # -------------------------------------------------
        # 1️⃣ Departments = Branches
        # -------------------------------------------------
        branch_names = ["CSE", "ECE", "ME", "CE"]
        departments = {}

        for name in branch_names:
            dept = db.query(models.Department).filter_by(dept_name=name).first()
            if not dept:
                dept = models.Department(dept_name=name)
                db.add(dept)
                db.flush()
            departments[name] = dept

        # -------------------------------------------------
        # 2️⃣ Rooms (≥ number of branches)
        # -------------------------------------------------
        for i in range(1, 9):
            room_name = f"Room-{100+i}"
            if not db.query(models.Room).filter_by(room_name=room_name).first():
                db.add(models.Room(room_name=room_name))

        # -------------------------------------------------
        # 3️⃣ Subjects (30 lectures per branch)
        # -------------------------------------------------
        branch_subjects = {
            "CSE": [
                ("CS101", "Programming", 6),
                ("CS102", "DSA", 6),
                ("CS103", "OS", 6),
                ("CS104", "DBMS", 6),
                ("CS105", "Maths", 6),
            ],
            "ECE": [
                ("EC101", "Circuits", 6),
                ("EC102", "Signals", 6),
                ("EC103", "VLSI", 6),
                ("EC104", "Control", 6),
                ("EC105", "Maths", 6),
            ],
            "ME": [
                ("ME101", "Thermodynamics", 6),
                ("ME102", "Mechanics", 6),
                ("ME103", "Manufacturing", 6),
                ("ME104", "CAD", 6),
                ("ME105", "Maths", 6),
            ],
            "CE": [
                ("CE101", "Structures", 6),
                ("CE102", "Geotechnical", 6),
                ("CE103", "Surveying", 6),
                ("CE104", "Transportation", 6),
                ("CE105", "Maths", 6),
            ],
        }

        subject_objs = []
        for branch, subjects in branch_subjects.items():
            for code, name, lectures in subjects:
                s = db.query(models.Subject).filter_by(subject_code=code).first()
                if not s:
                    s = models.Subject(
                        subject_code=code,
                        subject_name=name,
                        dept_id=departments[branch].dept_id,
                        lectures_per_week=lectures
                    )
                    db.add(s)
                    db.flush()
                subject_objs.append(s)

        # -------------------------------------------------
        # 4️⃣ Teachers (enough to cover branches)
        # -------------------------------------------------
        teacher_names = [
            "Dr. Sharma", "Prof. Verma", "Dr. Reddy",
            "Prof. Gill", "Dr. Kapoor", "Prof. Singh",
            "Dr. Joshi", "Prof. Das", "Rohit Sharma"
        ]

        teachers = []
        for name in teacher_names:
            t = db.query(models.Teacher).filter_by(teacher_name=name).first()
            if not t:
                t = models.Teacher(teacher_name=name)
                db.add(t)
                db.flush()
            teachers.append(t)

        # -------------------------------------------------
        # 5️⃣ Teacher–Subject mapping
        # -------------------------------------------------
        for i, sub in enumerate(subject_objs):
            teacher = teachers[i % len(teachers)]
            exists = db.query(models.TeacherSubject).filter_by(
                teacher_id=teacher.teacher_id,
                subject_id=sub.subject_id
            ).first()
            if not exists:
                db.add(models.TeacherSubject(
                    teacher_id=teacher.teacher_id,
                    subject_id=sub.subject_id
                ))

        # -------------------------------------------------
        # 6️⃣ Time Slots (5 days × 6 periods = 30)
        # -------------------------------------------------
        days = [
            models.DayOfWeekEnum.MONDAY,
            models.DayOfWeekEnum.TUESDAY,
            models.DayOfWeekEnum.WEDNESDAY,
            models.DayOfWeekEnum.THURSDAY,
            models.DayOfWeekEnum.FRIDAY,
        ]

        for day in days:
            for period in range(1, 7):
                exists = db.query(models.TimeSlot).filter_by(
                    day_of_week=day,
                    period_no=period
                ).first()
                if not exists:
                    db.add(models.TimeSlot(day_of_week=day, period_no=period))

        db.commit()
        print("🚀 Seed complete: FULL college timetable data ready!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_resources()