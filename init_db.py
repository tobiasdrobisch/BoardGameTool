from app.database import Base, engine
from app import models

# delete all tables
Base.metadata.drop_all(bind=engine)

# create all tables
Base.metadata.create_all(bind=engine)

print("succcessful reset of database!")