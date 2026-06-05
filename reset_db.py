from app.database import engine
from app import models


print("⚠️ DROPPING ALL TABLES (CASCADE)...")

models.Base.metadata.drop_all(bind=engine)

print("✅ ALL tables dropped completely.")


print("🔄 RECREATING ALL TABLES...")

models.Base.metadata.create_all(bind=engine)

print("✅ ALL tables recreated successfully.")