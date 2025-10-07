"""
Endpoints de gerenciamento de clientes.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/clients", tags=["Clientes"])


@router.post("", response_model=schemas.Client, status_code=status.HTTP_201_CREATED)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo cliente para o usuário autenticado.
    """
    return crud.create_user_client(db=db, client=client, user_id=current_user.id)


@router.get("", response_model=List[schemas.Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todos os clientes do usuário autenticado.
    """
    return crud.get_user_clients(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/{clientId}", response_model=schemas.Client)
def read_client(
    clientId: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna os dados de um cliente específico.
    """
    db_client = crud.get_client_by_id(
        db=db,
        client_id=clientId,
        user_id=current_user.id
    )
    if db_client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado ou permissão negada."
        )
    return db_client


@router.put("/{clientId}", response_model=schemas.Client)
def update_client(
    clientId: UUID,
    client: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza os dados de um cliente.
    """
    updated_client = crud.update_client(
        db=db,
        client_id=clientId,
        client_update=client,
        user_id=current_user.id
    )
    if updated_client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado ou permissão negada."
        )
    return updated_client


@router.delete("/{clientId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    clientId: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deleta um cliente.
    """
    deleted_client = crud.delete_client(
        db=db,
        client_id=clientId,
        user_id=current_user.id
    )
    if deleted_client is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado ou permissão negada."
        )
    return