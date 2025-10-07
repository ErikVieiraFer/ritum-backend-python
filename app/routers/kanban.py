"""
Endpoints do quadro Kanban (colunas e cartões).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="", tags=["Kanban"])


@router.get("/board/", response_model=List[schemas.TaskColumnWithCards])
def get_board(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todas as colunas e cartões do quadro Kanban do usuário.
    """
    return crud.get_board_for_user(db=db, user_id=current_user.id)


@router.post("/columns/", response_model=schemas.TaskColumn, status_code=status.HTTP_201_CREATED)
def create_column(
    column: schemas.TaskColumnCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria uma nova coluna no quadro Kanban.
    """
    return crud.create_task_column(db=db, column=column, user_id=current_user.id)


@router.patch("/columns/{column_id}", response_model=schemas.TaskColumn)
def update_column(
    column_id: int,
    column_update: schemas.TaskColumnUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza o título de uma coluna.
    """
    updated_column = crud.update_task_column(
        db=db,
        column_id=column_id,
        column_update=column_update,
        user_id=current_user.id
    )
    if updated_column is None:
        raise HTTPException(
            status_code=404,
            detail="Coluna não encontrada ou permissão negada."
        )
    return updated_column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(
    column_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deleta uma coluna e todos os seus cartões.
    """
    deleted_column = crud.delete_task_column(
        db=db,
        column_id=column_id,
        user_id=current_user.id
    )
    if deleted_column is None:
        raise HTTPException(
            status_code=404,
            detail="Coluna não encontrada ou permissão negada."
        )
    return


@router.post("/columns/{column_id}/cards/", response_model=schemas.TaskCard, status_code=status.HTTP_201_CREATED)
def create_card(
    column_id: int,
    card: schemas.TaskCardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo cartão em uma coluna.
    """
    db_card = crud.create_task_card(
        db=db,
        card=card,
        column_id=column_id,
        user_id=current_user.id
    )
    if db_card is None:
        raise HTTPException(
            status_code=404,
            detail="Coluna não encontrada ou não pertence ao usuário."
        )
    return db_card


@router.patch("/cards/{card_id}", response_model=schemas.TaskCard)
def update_card(
    card_id: int,
    card_update: schemas.TaskCardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza os detalhes de um cartão.
    """
    updated_card = crud.update_task_card(
        db=db,
        card_id=card_id,
        card_update=card_update,
        user_id=current_user.id
    )
    if updated_card is None:
        raise HTTPException(
            status_code=404,
            detail="Cartão não encontrado ou permissão negada."
        )
    return updated_card


@router.patch("/cards/{card_id}/move", response_model=schemas.TaskCard)
def move_card(
    card_id: int,
    move_data: schemas.TaskCardMove,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Move um cartão para outra coluna.
    """
    moved_card = crud.move_task_card(
        db=db,
        card_id=card_id,
        new_column_id=move_data.new_column_id,
        user_id=current_user.id
    )
    if moved_card is None:
        raise HTTPException(
            status_code=404,
            detail="Cartão ou coluna de destino não encontrados."
        )
    return moved_card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deleta um cartão.
    """
    deleted_card = crud.delete_task_card(
        db=db,
        card_id=card_id,
        user_id=current_user.id
    )
    if deleted_card is None:
        raise HTTPException(
            status_code=404,
            detail="Cartão não encontrado ou permissão negada."
        )
    return