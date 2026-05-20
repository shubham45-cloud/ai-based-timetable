from app.database import engine
from app import models

print("⚙️ Creating tables from models...")
models.Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully")
