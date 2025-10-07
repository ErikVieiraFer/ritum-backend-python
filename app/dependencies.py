"""
Dependências compartilhadas da API (autenticação, DB).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.database import SessionLocal

# Esquema de segurança: espera cabeçalho "Authorization: Bearer <token>"
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)


def get_db():
    """Cria uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Decodifica o token JWT e retorna o usuário autenticado.
    O token deve ser passado como: Authorization: Bearer <token>
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extrai o token do cabeçalho "Authorization: Bearer <token>"
    if token is None or not token.startswith("Bearer "):
        raise credentials_exception
    
    token_jwt = token.split(" ")[1]

    try:
        payload = jwt.decode(
            token_jwt,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user