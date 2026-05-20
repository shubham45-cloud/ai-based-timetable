from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
user = db.query(models.User).filter_by(email="admin@example.com").first()

if user:
    print(f"✅ User found: {user.email}")
    print(f"✅ Hashed password in DB: {user.password}")
    
    # Test verification
    is_correct = pwd_context.verify("admin123", user.password)
    print(f"❓ Does 'admin123' match? {is_correct}")
else:
    print("❌ User 'admin@example.com' not found in database.")

db.close()