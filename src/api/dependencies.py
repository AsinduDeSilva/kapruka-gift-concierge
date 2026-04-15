from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.api.db.core import get_db
from src.api.db.models import User
from src.api.schemas.auth import TokenData
from src.api.services.auth import SECRET_KEY, ALGORITHM
from src.agents.orchestrator import build_orchestrator, AgentOrchestrator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

agent_orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    global agent_orchestrator
    if agent_orchestrator is None:
        agent_orchestrator = build_orchestrator()
    return agent_orchestrator

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
