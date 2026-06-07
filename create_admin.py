from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

admin = models.User(
    name="Admin",
    email="admin@example.com",
    role="admin",
    password=pwd_context.hash("admin123")
)

db.add(admin)
db.commit()

print("Admin created successfully!")

db.close()