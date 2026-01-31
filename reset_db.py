import sys
import os

# Bulletproof path fix
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import SessionLocal


def reset_database():
    db = SessionLocal()
    try:
        print("🚀 Starting PostgreSQL database reset (branch-only mode)...")

        # Tables aligned with current models.py
        tables = [
            "timetable",
            "teacher_subjects",
            "subjects",
            "teachers",
            "rooms",
            "departments",
            "time_slots"
        ]

        table_string = ", ".join(tables)

        db.execute(
            text(f"TRUNCATE TABLE {table_string} RESTART IDENTITY CASCADE;")
        )
        db.commit()

        print("✅ Database reset successful. All IDs restarted from 1.")

    except Exception as e:
        db.rollback()
        print(f"❌ Reset failed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
