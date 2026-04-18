import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.infrastructure.config import PROJECT_ROOT


os.makedirs(f"{PROJECT_ROOT}/data/user_data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/user_data/storage.db"

engine = create_engine(DATABASE_URL)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
