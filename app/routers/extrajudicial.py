"""
Endpoints do assistente extrajudicial.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/extrajudicial-cases", tags=["Assistente Extrajudicial"])


@router.post("", response_model=schemas.CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case: schemas.CaseCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo caso extrajudicial (inventário, divórcio, usucapião).
    """
    return crud.create_extrajudicial_case(db=db, case=case, user_id=current_user.id)


@router.get("/{case_id}", response_model=schemas.CaseResponse)
def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna os dados de um caso extrajudicial.
    """
    db_case = crud.get_extrajudicial_case(db=db, case_id=case_id, user_id=current_user.id)
    if db_case is None:
        raise HTTPException(
            status_code=404,
            detail="Caso não encontrado ou permissão negada."
        )
    return db_case


@router.put("/{case_id}", response_model=schemas.CaseResponse)
def update_case(
    case_id: UUID,
    case_data: schemas.CaseUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza o campo data de um caso extrajudicial.
    """
    updated_case = crud.update_e