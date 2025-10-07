"""
CRUD de usuários.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import Tuple, Optional

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserPasswordUpdate
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Busca um usuário pelo ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Cria um novo usuário com senha criptografada."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
    """
    Autentica um usuário verificando email e senha.
    
    Returns:
        Tupla (user, error_code)
        error_code pode ser 'user_not_found' ou 'invalid_password'
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None, "user_not_found"
    if not verify_password(password, user.hashed_password):
        return None, "invalid_password"
    return user, None


def update_user_profile(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """Atualiza o perfil de um usuário."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    # Handle address separately (JSONB field)
    if 'address' in update_data and update_data['address'] is not None:
        db_user.address = update_data.pop('address')

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: User, password_update: UserPasswordUpdate) -> bool:
    """Atualiza a senha do usuário após verificar a senha atual."""
    if not verify_password(password_update.current_password, user.hashed_password):
        return False

    hashed_password = get_password_hash(password_update.new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return True