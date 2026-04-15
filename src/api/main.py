from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db.core import engine, Base
from src.api.routers import auth, chat
from dotenv import load_dotenv


load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kapruka Gift Concierge API",
    description="Backend service for Kapruka Gift Concierge AI Agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Welcome to Kapruka Gift Concierge API"}
