# from datetime import time
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app import models
# from app.models import (
#     Department,
#     Teacher,
#     Room,
#     TimeSlot,
#     Subject,
#     TeacherSubject,
#     CombinedSection,
#     DayOfWeekEnum,
#     RoomTypeEnum,
#     SubjectTypeEnum,
# )

# from app.core.security import get_password_hash


# # ══════════════════════════════════════════════════════════════════════════════
# # MASTER DATA
# # ══════════════════════════════════════════════════════════════════════════════

# DEPARTMENTS = [
#     (1, "CSE_4A"),
#     (2, "CSE_4B"),
#     (3, "CSE_4C"),
#     (4, "CSE_6A"),
#     (5, "CSE_6B"),
#     (6, "CSE_8A"),
#     (7, "CSE_4ABC"),
#     (8, "CSE_6AB"),
# ]

# COMBINED_SECTION_LINKS = [
#     (7, 1),
#     (7, 2),
#     (7, 3),
#     (8, 4),
#     (8, 5),
# ]

# TEACHERS = [
#     (1, "Dr. Arun Kumar Tripathi"),
#     (2, "Dr. Sangeeta Arora"),
#     (3, "Mr. Vivek Ranjan"),
# ]

# ROOMS = [
#     (1, "CR-101", RoomTypeEnum.CLASSROOM),
#     (2, "CR-102", RoomTypeEnum.CLASSROOM),
#     (3, "LAB-101", RoomTypeEnum.LAB),
# ]

# _PERIOD_TIMES = [
#     (1, time(8, 0), time(9, 0)),
#     (2, time(9, 0), time(10, 0)),
#     (3, time(10, 15), time(11, 15)),
#     (4, time(11, 15), time(12, 15)),
# ]

# _DAYS = [
#     DayOfWeekEnum.MONDAY,
#     DayOfWeekEnum.TUESDAY,
#     DayOfWeekEnum.WEDNESDAY,
#     DayOfWeekEnum.THURSDAY,
#     DayOfWeekEnum.FRIDAY,
#     DayOfWeekEnum.SATURDAY,
# ]

# T = SubjectTypeEnum.THEORY
# L = SubjectTypeEnum.LAB

# SUBJECTS = [
#     (101, "BCSE0402_4A", "DBMS", 3, 1, 3, T, False),
#     (102, "BCSE0401_4A", "DSA-II", 3, 1, 3, T, False),
#     (103, "BCSE0452_4A", "DBMS Lab", 2, 1, 2, L, False),
# ]

# TEACHER_SUBJECTS = [
#     (1, 101),
#     (2, 102),
#     (3, 103),
# ]


# # ══════════════════════════════════════════════════════════════════════════════
# # SEED FUNCTION
# # ══════════════════════════════════════════════════════════════════════════════

# def seed_college_data(db: Session):

#     try:
#         # ════════════════════════════════════════════════════════════════════
#         # CLEAR TABLES
#         # ════════════════════════════════════════════════════════════════════

#         db.query(models.Timetable).delete()
#         db.query(models.TeacherSubject).delete()
#         db.query(models.CombinedSection).delete()
#         db.query(models.Subject).delete()
#         db.query(models.Room).delete()
#         db.query(models.TimeSlot).delete()
#         db.query(models.Teacher).delete()
#         db.query(models.Department).delete()

#         # Delete users also
#         db.query(models.User).delete()

#         db.commit()

#         # ════════════════════════════════════════════════════════════════════
#         # DEPARTMENTS
#         # ════════════════════════════════════════════════════════════════════

#         for dept_id, dept_name in DEPARTMENTS:
#             db.add(
#                 Department(
#                     dept_id=dept_id,
#                     dept_name=dept_name
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # COMBINED SECTIONS
#         # ════════════════════════════════════════════════════════════════════

#         for combined_id, constituent_id in COMBINED_SECTION_LINKS:
#             db.add(
#                 CombinedSection(
#                     combined_dept_id=combined_id,
#                     constituent_dept_id=constituent_id
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # TEACHERS
#         # ════════════════════════════════════════════════════════════════════

#         for teacher_id, teacher_name in TEACHERS:
#             db.add(
#                 Teacher(
#                     teacher_id=teacher_id,
#                     teacher_name=teacher_name,
#                     dept_id=1
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # ROOMS
#         # ════════════════════════════════════════════════════════════════════

#         for room_id, room_name, room_type in ROOMS:
#             db.add(
#                 Room(
#                     room_id=room_id,
#                     room_name=room_name,
#                     room_type=room_type
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # TIME SLOTS
#         # ════════════════════════════════════════════════════════════════════

#         slot_id = 1

#         for day in _DAYS:
#             for period, start_time, end_time in _PERIOD_TIMES:

#                 db.add(
#                     TimeSlot(
#                         timeslot_id=slot_id,
#                         day_of_week=day,
#                         period_no=period,
#                         start_time=start_time,
#                         end_time=end_time,
#                     )
#                 )

#                 slot_id += 1

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # SUBJECTS
#         # ════════════════════════════════════════════════════════════════════

#         for (
#             subject_id,
#             subject_code,
#             subject_name,
#             credits,
#             dept_id,
#             lectures_per_week,
#             subject_type,
#             is_online
#         ) in SUBJECTS:

#             db.add(
#                 Subject(
#                     subject_id=subject_id,
#                     subject_code=subject_code,
#                     subject_name=subject_name,
#                     credits=credits,
#                     dept_id=dept_id,
#                     lectures_per_week=lectures_per_week,
#                     subject_type=subject_type,
#                     is_online=is_online,
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # TEACHER SUBJECT MAPPING
#         # ════════════════════════════════════════════════════════════════════

#         for idx, (teacher_id, subject_id) in enumerate(
#             TEACHER_SUBJECTS,
#             start=1
#         ):

#             db.add(
#                 TeacherSubject(
#                     ts_id=idx,
#                     teacher_id=teacher_id,
#                     subject_id=subject_id
#                 )
#             )

#         db.flush()

#         # ════════════════════════════════════════════════════════════════════
#         # ADMIN USER
#         # ════════════════════════════════════════════════════════════════════

#         admin_user = models.User(
#             name="Admin",
#             email="admin@gmail.com",
#             role="admin",
#             password=get_password_hash("admin123")
            
#         )

#         db.add(admin_user)

#         # ════════════════════════════════════════════════════════════════════
#         # FINAL COMMIT
#         # ════════════════════════════════════════════════════════════════════

#         db.commit()

#         print("\n✅ DATABASE SEEDED SUCCESSFULLY")

#         return {
#             "status": "success"
#         }

#     except Exception as e:

#         db.rollback()

#         print(f"\n❌ ERROR: {str(e)}")

#         return {
#             "status": "error",
#             "message": str(e)
#         }


# # ══════════════════════════════════════════════════════════════════════════════
# # MAIN EXECUTION
# # ══════════════════════════════════════════════════════════════════════════════

# if __name__ == "__main__":

#     db = SessionLocal()

#     try:
#         result = seed_college_data(db)

#         print(result)

#     finally:
#         db.close()
"""
seed_data.py  –  NIET Greater Noida  |  CSE Dept  |  Even Semester 2025-26
══════════════════════════════════════════════════════════════════════════════

DATA SOURCED FROM: Faculty Load Distribution PDF (Even Sem 2025-26)

SECTIONS
  4A, 4B, 4C  →  Semester IV (3 sections)
  6A, 6B      →  Semester VI (2 sections)
  8A          →  Semester VIII (ALL ONLINE – skipped by AI engine)
  4ABC        →  Virtual combined section (AICE / FoCys / Django taught together)
  6AB         →  Virtual combined section (SMA / AJP / PDA / MEAN taught together)

ROOMS
  5 Classrooms : CR-101 … CR-105
  3 Labs       : LAB-101, LAB-102, LAB-103

TIME SLOTS
  Periods 1-8 per day, Monday–Saturday
  Pairs for labs: (P1,P2), (P3,P4), (P5,P6), (P7,P8)

SUBJECT FIELD MEANINGS
  THEORY  : lectures_per_week = L + T  (separate single-period classroom slots)
  LAB     : lectures_per_week = P / 2  (each = one 2-hour consecutive lab session)
══════════════════════════════════════════════════════════════════════════════
"""

from datetime import time
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.models import (
    Department,
    Teacher,
    Room,
    TimeSlot,
    Subject,
    TeacherSubject,
    CombinedSection,
    DayOfWeekEnum,
    RoomTypeEnum,
    SubjectTypeEnum,
)

from app.core.security import get_password_hash


# ══════════════════════════════════════════════════════════════════════════════
#  MASTER DATA TABLES
# ══════════════════════════════════════════════════════════════════════════════

DEPARTMENTS = [
    # id  name
    (1,  "CSE_4A"),
    (2,  "CSE_4B"),
    (3,  "CSE_4C"),
    (4,  "CSE_6A"),
    (5,  "CSE_6B"),
    (6,  "CSE_8A"),      # all-online, skipped by engine
    (7,  "CSE_4ABC"),    # virtual combined – 4A+4B+4C
    (8,  "CSE_6AB"),     # virtual combined – 6A+6B
]

# combined_dept_id → [constituent_dept_ids]
COMBINED_SECTION_LINKS = [
    (7, 1), (7, 2), (7, 3),   # 4ABC → 4A, 4B, 4C
    (8, 4), (8, 5),            # 6AB  → 6A, 6B
]

TEACHERS = [
    # id   name
    (1,  "Dr. Arun Kumar Tripathi"),
    (2,  "Dr. Sangeeta Arora"),
    (3,  "Mr. Vivek Ranjan"),
    (4,  "Dr. Deepak Upreti"),
    (5,  "Dr. Kanika Singhal"),
    (6,  "Dr. Divya Singhal"),
    (7,  "Ms. Nishu Niharika"),
    (8,  "Mr. Ajay Kumar"),
    (9,  "Ms. Pooja Sharma"),       # Pooja-I
    (10, "Ms. Madhu"),
    (11, "Mr. Anshul Varshney"),
    (12, "Ms. Pooja Gupta"),        # Pooja-II
    (13, "Mr. Anurag Mishra"),
    (14, "Ms. Arhina Ghosh"),
    (15, "Ms. Bharti Kaushik"),
    (16, "Mr. Apoorv Jain"),
    (17, "Ms. Prashansa"),
]

# 5 classrooms + 3 labs  (user-specified)
ROOMS = [
    # id   name         type
    (1,  "CR-101",   RoomTypeEnum.CLASSROOM),
    (2,  "CR-102",   RoomTypeEnum.CLASSROOM),
    (3,  "CR-103",   RoomTypeEnum.CLASSROOM),
    (4,  "CR-104",   RoomTypeEnum.CLASSROOM),
    (5,  "CR-105",   RoomTypeEnum.CLASSROOM),
    (6,  "LAB-101",  RoomTypeEnum.LAB),
    (7,  "LAB-102",  RoomTypeEnum.LAB),
    (8,  "LAB-103",  RoomTypeEnum.LAB),
]

# 8 periods per day, Mon–Sat  (48 total time-slot rows)
_PERIOD_TIMES = [
    (1, time(8,  0),  time(9,  0)),
    (2, time(9,  0),  time(10, 0)),
    (3, time(10, 15), time(11, 15)),   # 15-min break between P2 & P3
    (4, time(11, 15), time(12, 15)),
    (5, time(13, 0),  time(14, 0)),    # 45-min lunch after P4
    (6, time(14, 0),  time(15, 0)),
    (7, time(15, 15), time(16, 15)),   # 15-min break between P6 & P7
    (8, time(16, 15), time(17, 15)),
]
_DAYS = [
    DayOfWeekEnum.MONDAY,
    DayOfWeekEnum.TUESDAY,
    DayOfWeekEnum.WEDNESDAY,
    DayOfWeekEnum.THURSDAY,
    DayOfWeekEnum.FRIDAY,
    
]

# ─────────────────────────────────────────────────────────────────────────────
# SUBJECTS
# Columns:
#   (subject_id, code, name, credits, dept_id, lpw, type, is_online)
#   lpw = lectures_per_week
#       THEORY → L+T (single-period count)
#       LAB    → P/2 (2-hour session count)
# ─────────────────────────────────────────────────────────────────────────────
T = SubjectTypeEnum.THEORY
L = SubjectTypeEnum.LAB

SUBJECTS = [
    # ══ COMBINED 4th sem  (dept 7 = CSE_4ABC) ════════════════════════════════
    #  Subject     code              name              cr  dept  lpw  type  online
    (101, "BNC0401Y_4ABC",  "AICE",                   2,  7,    2,   T,    False),
    (102, "BCSCY0411_4ABC", "Foundations of CyberSec",3,  7,    3,   T,    False),
    (103, "BCSE0411_4ABC",  "Django Framework",        3,  7,    3,   T,    False),

    # ══ SECTION 4A  (dept 1) ═════════════════════════════════════════════════
    # Theory
    (111, "BCSE0402_4A",    "DBMS",                   3,  1,    3,   T,    False),
    (112, "BCSE0401_4A",    "DSA-II",                 3,  1,    3,   T,    False),
    (113, "BCS0402_4A",     "Big Data Analytics",     3,  1,    3,   T,    False),
    (114, "BCSAI0411_4A",   "Data Analytics",         3,  1,    3,   T,    False),
    # Labs  (lpw = P/2)
    (115, "BCSE0452Z_4A",   "DBMS Lab",               2,  1,    2,   L,    False),
    (116, "BCSE0451_4A",    "DSA-II Lab",             2,  1,    2,   L,    False),
    (117, "BCSE0455_4A",    "Web Tech Lab",           3,  1,    3,   L,    False),
    (118, "BCSE0459_4A",    "Mini Project",           1,  1,    1,   L,    False),

    # ══ SECTION 4B  (dept 2) ═════════════════════════════════════════════════
    # Theory
    (121, "BCSE0402_4B",    "DBMS",                   3,  2,    3,   T,    False),
    (122, "BCSE0401_4B",    "DSA-II",                 3,  2,    3,   T,    False),
    (123, "BCS0402_4B",     "Big Data Analytics",     3,  2,    3,   T,    False),
    (124, "BCSAI0411_4B",   "Data Analytics",         3,  2,    3,   T,    False),
    # Labs
    (125, "BCSE0452Z_4B",   "DBMS Lab",               2,  2,    2,   L,    False),
    (126, "BCSE0451_4B",    "DSA-II Lab",             2,  2,    2,   L,    False),
    (127, "BCSE0455_4B",    "Web Tech Lab",           3,  2,    3,   L,    False),
    (128, "BCSE0459_4B",    "Mini Project",           1,  2,    1,   L,    False),

    # ══ SECTION 4C  (dept 3) ═════════════════════════════════════════════════
    # Theory
    (131, "BCSE0402_4C",    "DBMS",                   3,  3,    3,   T,    False),
    (132, "BCSE0401_4C",    "DSA-II",                 3,  3,    3,   T,    False),
    (133, "BCS0402_4C",     "Big Data Analytics",     3,  3,    3,   T,    False),
    (134, "BCSAI0411_4C",   "Data Analytics",         3,  3,    3,   T,    False),
    # Labs
    (135, "BCSE0452Z_4C",   "DBMS Lab",               2,  3,    2,   L,    False),
    (136, "BCSE0451_4C",    "DSA-II Lab",             2,  3,    2,   L,    False),
    (137, "BCSE0455_4C",    "Web Tech Lab",           3,  3,    3,   L,    False),
    (138, "BCSE0459_4C",    "Mini Project",           1,  3,    1,   L,    False),

    # ══ COMBINED 6th sem  (dept 8 = CSE_6AB) ═════════════════════════════════
    (201, "BCSAI0622_6AB",  "Statistical Methods & Analytics", 3, 8, 4, T, False),
    (202, "BCSAI0612_6AB",  "Advanced Java Programming",       3, 8, 4, T, False),
    (203, "BCSAI0617_6AB",  "Predictive Data Analytics",       3, 8, 4, T, False),
    (204, "BCSE0614_6AB",   "MEAN Stack Development",          3, 8, 4, T, False),

    # ══ SECTION 6A  (dept 4) ═════════════════════════════════════════════════
    # Theory
    (211, "BCSML0601_6A",   "Machine Learning",       4,  4,    4,   T,    False),
    # Labs  (lpw = P/2)
    (215, "BCSML0651_6A",   "ML Lab",                 1,  4,    1,   L,    False),
    (216, "BCSE0653_6A",    "Software Engineering & Design Lab", 3, 4, 3, L, False),
    (217, "BCS0601_6A",     "Cloud Application Dev Lab",        3, 4, 3, L, False),
    (218, "BCSE0659_6A",    "Mini Project",           2,  4,    2,   L,    False),

    # ══ SECTION 6B  (dept 5) ═════════════════════════════════════════════════
    # Theory
    (221, "BCSML0601_6B",   "Machine Learning",       4,  5,    4,   T,    False),
    # Labs
    (225, "BCSML0651_6B",   "ML Lab",                 1,  5,    1,   L,    False),
    (226, "BCSE0653_6B",    "Software Engineering & Design Lab", 3, 5, 3, L, False),
    (227, "BCS0601_6B",     "Cloud Application Dev Lab",        3, 5, 3, L, False),
    (228, "BCSE0659_6B",    "Mini Project",           2,  5,    2,   L,    False),

    # ══ SECTION 8A  (dept 6) – ALL ONLINE ════════════════════════════════════
    (301, "ACSE0858_8A",    "Industrial Internship",  20, 6,    0,   L,    True),
    (302, "ACSE0859_8A",    "Capstone Project",       20, 6,    0,   L,    True),
    (303, "AOE0866_8A",     "Skill Enhancement",      2,  6,    0,   T,    True),
]

# ─────────────────────────────────────────────────────────────────────────────
# TEACHER ↔ SUBJECT ASSIGNMENTS
# (teacher_id, subject_id)
# One entry = teacher is qualified / assigned to teach that subject-section.
# For subjects shared between sub-groups the first entry is used by the engine.
# ─────────────────────────────────────────────────────────────────────────────
TEACHER_SUBJECTS = [
    # ── Combined 4th sem ─────────────────────────────────────────────────────
    (1,  101),   # Dr. Arun   → AICE (combined 4ABC)
    (4,  102),   # Dr. Deepak → FoCys (combined 4ABC)
    (11, 103),   # Mr. Anshul → Django (combined 4ABC)

    # ── Section 4A theory ────────────────────────────────────────────────────
    (1,  111),   # Dr. Arun   → DBMS 4A
    (1,  112),   # Dr. Arun   → DSA-II 4A
    (3,  113),   # Vivek      → BDA 4A
    (12, 114),   # Pooja-II   → Data Analytics 4A

    # ── Section 4A labs ──────────────────────────────────────────────────────
    (15, 115),   # Bharti     → DBMS Lab 4A
    (3,  116),   # Vivek      → DSA-II Lab 4A
    (9,  117),   # Pooja-I    → Web Tech Lab 4A
    (2,  118),   # Dr. Sangeeta → Mini Project 4A

    # ── Section 4B theory ────────────────────────────────────────────────────
    (15, 121),   # Bharti     → DBMS 4B
    (4,  122),   # Dr. Deepak → DSA-II 4B
    (10, 123),   # Madhu      → BDA 4B
    (17, 124),   # Prashansa  → Data Analytics 4B

    # ── Section 4B labs ──────────────────────────────────────────────────────
    (13, 125),   # Anurag     → DBMS Lab 4B
    (7,  126),   # Nishu      → DSA-II Lab 4B
    (3,  127),   # Vivek      → Web Tech Lab 4B
    (4,  128),   # Dr. Deepak → Mini Project 4B

    # ── Section 4C theory ────────────────────────────────────────────────────
    (13, 131),   # Anurag     → DBMS 4C
    (5,  132),   # Dr. Kanika → DSA-II 4C
    (6,  133),   # Dr. Divya  → BDA 4C
    (17, 134),   # Prashansa  → Data Analytics 4C

    # ── Section 4C labs ──────────────────────────────────────────────────────
    (14, 135),   # Arhina     → DBMS Lab 4C
    (8,  136),   # Ajay       → DSA-II Lab 4C
    (10, 137),   # Madhu      → Web Tech Lab 4C
    (5,  138),   # Dr. Kanika → Mini Project 4C

    # ── Combined 6th sem ─────────────────────────────────────────────────────
    (2,  201),   # Dr. Sangeeta → SMA (6AB)
    (3,  202),   # Vivek      → AJP (6AB)
    (4,  203),   # Dr. Deepak → PDA (6AB)
    (11, 204),   # Anshul     → MEAN Stack (6AB)

    # ── Section 6A theory ────────────────────────────────────────────────────
    (1,  211),   # Dr. Arun   → ML 6A

    # ── Section 6A labs ──────────────────────────────────────────────────────
    (1,  215),   # Dr. Arun   → ML Lab 6A
    (2,  216),   # Dr. Sangeeta → SED Lab 6A
    (15, 217),   # Bharti     → CAD Lab 6A
    (14, 218),   # Arhina     → Mini Project 6A

    # ── Section 6B theory ────────────────────────────────────────────────────
    (3,  221),   # Vivek      → ML 6B

    # ── Section 6B labs ──────────────────────────────────────────────────────
    (3,  225),   # Vivek      → ML Lab 6B
    (2,  226),   # Dr. Sangeeta → SED Lab 6B
    (13, 227),   # Anurag     → CAD Lab 6B
    (9,  228),   # Pooja-I    → Mini Project 6B

    # ── 8th sem online (assigned for record-keeping, engine skips them) ──────
    (1,  302),   # Dr. Arun   → Capstone 8A
    (3,  302),   # Vivek      → Capstone 8A  (co-supervisor)
    (1,  303),   # Dr. Arun   → Skill Enhancement 8A
]


# ══════════════════════════════════════════════════════════════════════════════
#  SEED FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def seed_college_data(db: Session) -> dict:
    """
    Wipes and re-seeds ALL reference data.
    Call once via init_db.py or a dedicated /admin/seed endpoint.
    """
    try:
        # ── Clear in FK-safe order ────────────────────────────────────────────
        db.query(models.Timetable).delete()
        db.query(models.TeacherSubject).delete()
        db.query(models.CombinedSection).delete()
        db.query(models.Subject).delete()
        db.query(models.Room).delete()
        db.query(models.TimeSlot).delete()
        db.query(models.Teacher).delete()
        db.query(models.Department).delete()
        db.commit()

        # ── Departments ───────────────────────────────────────────────────────
        for dept_id, name in DEPARTMENTS:
            db.add(Department(dept_id=dept_id, dept_name=name))
        db.flush()

        # ── Combined section links ─────────────────────────────────────────────
        for comb_id, const_id in COMBINED_SECTION_LINKS:
            db.add(CombinedSection(combined_dept_id=comb_id, constituent_dept_id=const_id))
        db.flush()

        # ── Teachers ──────────────────────────────────────────────────────────
        # All teachers belong to the main CSE dept (dept 1 used as home dept)
        for t_id, t_name in TEACHERS:
            db.add(Teacher(teacher_id=t_id, teacher_name=t_name, dept_id=1))
        db.flush()

        # ── Rooms ─────────────────────────────────────────────────────────────
        for r_id, r_name, r_type in ROOMS:
            db.add(Room(room_id=r_id, room_name=r_name, room_type=r_type))
        db.flush()

        # ── Time slots (8 per day × 6 days = 48 rows) ─────────────────────────
        slot_id = 1
        for day in _DAYS:
            for (period, start, end) in _PERIOD_TIMES:
                db.add(TimeSlot(
                    timeslot_id=slot_id,
                    day_of_week=day,
                    period_no=period,
                    start_time=start,
                    end_time=end,
                ))
                slot_id += 1
        db.flush()

        # ── Subjects ──────────────────────────────────────────────────────────
        for (sid, code, name, credits, dept_id, lpw, stype, is_online) in SUBJECTS:
            db.add(Subject(
                subject_id=sid,
                subject_code=code,
                subject_name=name,
                credits=credits,
                dept_id=dept_id,
                lectures_per_week=lpw,
                subject_type=stype,
                is_online=is_online,
            ))
        db.flush()

        # ── Teacher–subject links ──────────────────────────────────────────────
        for idx, (t_id, s_id) in enumerate(TEACHER_SUBJECTS, start=1):
            db.add(TeacherSubject(ts_id=idx, teacher_id=t_id, subject_id=s_id))
        db.flush()
        admin_user = models.User(
            name="Admin",             
            email="admin@gmail.com",
            role="admin",
            password=get_password_hash("admin123")
            
        )
        
        db.add(admin_user)
        db.commit()

        # ── Summary ───────────────────────────────────────────────────────────
        return {
            "status": "success",
            "seeded": {
                "departments": len(DEPARTMENTS),
                "teachers":    len(TEACHERS),
                "rooms":       len(ROOMS),
                "time_slots":  slot_id - 1,
                "subjects":    len(SUBJECTS),
                "teacher_subject_links": len(TEACHER_SUBJECTS),
                "combined_links": len(COMBINED_SECTION_LINKS),
            }
        }

    except Exception as exc:
        db.rollback()
        return {"status": "error", "message": str(exc)}


# ── Quick teacher load verification (run this offline to debug) ──────────────
def print_teacher_load_summary():
    """
    Prints expected weekly contact periods per teacher.
    Run stand-alone:  python -c "from app.seed_data import print_teacher_load_summary; print_teacher_load_summary()"
    """
    teacher_names = dict(TEACHERS)
    subject_lpw   = {sid: lpw  for (sid, _, _, _, _, lpw, stype, _) in SUBJECTS}
    subject_type  = {sid: stype for (sid, _, _, _, _, lpw, stype, _) in SUBJECTS}

    load: dict[int, int] = {}
    for t_id, s_id in TEACHER_SUBJECTS:
        lpw   = subject_lpw.get(s_id, 0)
        stype = subject_type.get(s_id, SubjectTypeEnum.THEORY)
        # lab sessions count double (2 periods per session)
        contact = lpw * 2 if stype == SubjectTypeEnum.LAB else lpw
        load[t_id] = load.get(t_id, 0) + contact

    print("\n─── TEACHER WEEKLY CONTACT PERIODS ───")
    for t_id, name in sorted(TEACHERS):
        periods = load.get(t_id, 0)
        flag = "  ⚠️  OVERLOADED" if periods > 24 else ""
        print(f"  {name:<35} {periods:>3} periods/week{flag}")
    print("─" * 50)
    print(f"  Max allowed: 4 periods/day × 6 days = 24\n")



if __name__ == "__main__":

    db = SessionLocal()

    try:
        result = seed_college_data(db)
        print(result)

    finally:
        db.close()