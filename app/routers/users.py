"""
Endpoints de perfil de usuário.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Retorna os dados do usuário autenticado.
    """
    return current_user


@router.patch("/me", response_model=schemas.User)
def update_users_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza o perfil do usuário autenticado.
    """
    updated_user = crud.update_user_profile(
        db=db,
        user_id=current_user.id,
        user_update=user_update
    )
    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )
    return updated_user


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    password_update: schemas.UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza a senha do usuário autenticado.
    """
    success = crud.update_user_password(
        db=db,
        user=current_user,
        password_update=password_update
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Senha atual incorreta."
        )
    return