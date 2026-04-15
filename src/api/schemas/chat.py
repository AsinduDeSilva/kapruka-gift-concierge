from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    user_query: str

class ChatResponse(BaseModel):
    reply: str

class SessionResponse(BaseModel):
    session_id: str
