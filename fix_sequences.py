import sys
import os
from sqlalchemy import text
from app.database import SessionLocal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def master_reset():
    db = SessionLocal()
    try:
        print("🚀 Resetting all tables and ID counters...")
        # Added 'time_slots' to the list to fix the primary key error
        tables = [
            "timetable", "teacher_subjects", "time_slots", 
            "sections", "rooms", "teachers", "subjects", "departments"
        ]
        db.rollback() 
        table_string = ", ".join(tables)
        db.execute(text(f"TRUNCATE TABLE {table_string} RESTART IDENTITY CASCADE;"))
        db.commit()
        print("✅ Success! Tables are empty and IDs are back to 1.")
    except Exception as e:
        db.rollback()
        print(f"❌ Reset failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    master_reset()