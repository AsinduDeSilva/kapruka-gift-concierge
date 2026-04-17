from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    session_id: str
    user_query: str

class SessionResponse(BaseModel):
    session_id: str

class ProfileResponse(BaseModel):
    profile: Optional[Dict[str, Any]] = None