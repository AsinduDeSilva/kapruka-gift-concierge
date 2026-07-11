import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.infrastructure.config import DB_SSL_MODE, DATABASE_URL
if not DATABASE_URL:
    raise ValueError("POSTGRESQL_DB_URL is not set")

connect_args = {}
if DB_SSL_MODE and DB_SSL_MODE != "disable":
    connect_args["sslmode"] = DB_SSL_MODE

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
