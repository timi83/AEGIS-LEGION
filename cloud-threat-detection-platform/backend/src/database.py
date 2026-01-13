# src/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get DB URL from environment or fallback to SQLite for local development
# Get DB URL from environment or fallback to Postgres for local development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ctdirp_db") # Update in propduction

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declare base model
Base = declarative_base()


def init_db():
    """
    Import model metadata and create database tables.
    """
    from src.models.incident import Incident
    from src.models.rule import Rule
    from src.models.user import User

    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency for getting a DB session per request.
    """
    print("DEBUG: get_db called - Creating Session")
    try:
        db = SessionLocal()
        print("DEBUG: Session created")
        try:
            yield db
        finally:
            print("DEBUG: Closing Session")
            db.close()
    except Exception as e:
        print(f"DEBUG: CRASH in get_db: {e}")
        raise e
