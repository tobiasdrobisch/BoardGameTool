from app.database import engine, Base
import app.models

print("⚠️ DROPPING ALL TABLES IN DEV DB")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ DEV DB recreated")
