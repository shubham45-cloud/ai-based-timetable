# refresh_db.py
import sys
import os

# Appends your current directory to path so python can locate the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base  # Adjust import paths to match your exact file structure
from app.models import TimetableVersion, Timetable  # Ensures models are registered

def wipe_and_rebuild():
    print("Connecting to PostgreSQL and dropping stale tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Re-building tables with the updated schema definitions...")
    Base.metadata.create_all(bind=engine)
    print("🚀 Database successfully synchronized!")

if __name__ == "__main__":
    wipe_and_rebuild()