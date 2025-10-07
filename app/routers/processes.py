"""
Endpoints de gerenciamento de processos.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/processes", tags=["Processos"])


@router.post("/", response_model=schemas.Process, status_code=status.HTTP_201_CREATED)
def create_process(
    process: schemas.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo processo para o usuário autenticado.
    """
    return crud.create_user_process(db=db, process=process, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Process])
def read_processes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todos os processos do usuário autenticado.
    """
    return crud.get_user_processes(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )