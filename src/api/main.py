from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv


load_dotenv()

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

@app.get("/")
def root():
    return {"message": "Welcome to Kapruka Gift Concierge API"}
