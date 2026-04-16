from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.db.core import get_db
from src.api.db.models import User, Message, ChatSession
from src.api.schemas.chat import ChatRequest, ChatResponse, SessionResponse, ProfileResponse
from src.api.dependencies import get_current_user, get_orchestrator
from src.agents.orchestrator import AgentOrchestrator
from src.memory.semantic_memory_manager import SemanticMemoryManager
from src.memory.short_term_memory_manager import ShortTermMemoryManager

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/session", response_model=SessionResponse)
def create_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(user_id=user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(session_id=session.id)

@router.get("/profile", response_model=ProfileResponse)
def get_user_profile(
    user: User = Depends(get_current_user),
    semantic_memory: SemanticMemoryManager = Depends(SemanticMemoryManager)
):
    return ProfileResponse(profile=semantic_memory.get_profile(str(user.id)))

@router.post("", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):

    session = db.query(ChatSession).filter(
        ChatSession.id == request.session_id,
        ChatSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_messages = db.query(Message).filter(
        Message.session_id == request.session_id
    ).order_by(Message.created_at.asc()).all()

    st_memory = ShortTermMemoryManager()
    for msg in db_messages:
        st_memory.add_message(msg.role, msg.content)

    reply_text = agent_orchestrator.chat(
        user_id=str(user.id),
        user_query=request.user_query,
        st_memory=st_memory
    )
    
    db.add(Message(session_id=request.session_id, role="user", content=request.user_query))
    db.add(Message(session_id=request.session_id, role="assistant", content=reply_text))
    db.commit()

    updated_profile = agent_orchestrator.semantic_memory.get_profile(str(user.id))

    return ChatResponse(reply=reply_text, profile=updated_profile)
