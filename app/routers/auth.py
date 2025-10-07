"""
Endpoints de autenticação (login, signup, refresh token).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.dependencies import get_db

router = APIRouter(prefix="", tags=["Autenticação"])


@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário (signup).
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Este email já está cadastrado."
        )
    return crud.create_user(db=db, user=user)


@router.post("/token", response_model=schemas.TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna access_token + refresh_token.
    """
    user, error = crud.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password
    )
    
    if error == "user_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário com este email não foi encontrado.",
        )
    if error == "invalid_password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A senha fornecida está incorreta.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gerar ambos os tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/token/refresh", response_model=schemas.TokenResponse)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Renova o access token usando um refresh token válido.
    Implementa Refresh Token Rotation (RTR).
    """
    payload = decode_refresh_token(refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido.",
        )
    
    # Validar se usuário ainda existe
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    
    # Gerar novos tokens (RTR)
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }