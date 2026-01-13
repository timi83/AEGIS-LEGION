from src.database import engine, Base
from src.models.user import User
from src.models.incident import Incident

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")
