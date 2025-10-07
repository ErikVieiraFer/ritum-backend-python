"""
CRUD do quadro Kanban.
"""

from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from typing import List, Optional

from app.models import TaskColumn, TaskCard
from app.schemas import TaskColumnCreate, TaskColumnUpdate, TaskCardCreate, TaskCardUpdate


def get_board_for_user(db: Session, user_id: UUID) -> List[TaskColumn]:
    """
    Busca todas as colunas e cartões de um usuário.
    Usa selectinload para evitar N+1 queries.
    """
    return (
        db.query(TaskColumn)
        .filter(TaskColumn.owner_id == user_id)
        .order_by(TaskColumn.position)
        .options(selectinload(TaskColumn.cards))
        .all()
    )


def create_task_column(db: Session, column: TaskColumnCreate, user_id: UUID) -> TaskColumn:
    """Cria uma nova coluna."""
    db_column = TaskColumn(**column.model_dump(), owner_id=user_id)
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column


def update_task_column(db: Session, column_id: int, column_update: TaskColumnUpdate, user_id: UUID) -> Optional[TaskColumn]:
    """Atualiza o título de uma coluna."""
    db_column = db.query(TaskColumn).filter(
        TaskColumn.id == column_id,
        TaskColumn.owner_id == user_id
    ).first()

    if not db_column:
        return None

    db_column.title = column_update.title
    db.commit()
    db.refresh(db_column)
    return db_column


def delete_task_column(db: Session, column_id: int, user_id: UUID) -> Optional[TaskColumn]:
    """Deleta uma coluna."""
    column_to_delete = db.query(TaskColumn).filter(
        TaskColumn.id == column_id,
        TaskColumn.owner_id == user_id
    ).first()

    if not column_to_delete:
        return None
    
    db.delete(column_to_delete)
    db.commit()
    return column_to_delete


def create_task_card(db: Session, card: TaskCardCreate, column_id: int, user_id: UUID) -> Optional[TaskCard]:
    """Cria um novo cartão em uma coluna."""
    db_column = db.query(TaskColumn).filter(
        TaskColumn.id == column_id,
        TaskColumn.owner_id == user_id
    ).first()

    if not db_column:
        return None

    db_card = TaskCard(**card.model_dump(), column_id=column_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def update_task_card(db: Session, card_id: int, card_update: TaskCardUpdate, user_id: UUID) -> Optional[TaskCard]:
    """Atualiza os detalhes de um cartão."""
    db_card = (
        db.query(TaskCard)
        .join(TaskColumn, TaskCard.column_id == TaskColumn.id)
        .filter(
            TaskCard.id == card_id,
            TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not db_card:
        return None
    
    update_data = card_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_card, key, value)
        
    db.commit()
    db.refresh(db_card)
    return db_card


def delete_task_card(db: Session, card_id: int, user_id: UUID) -> Optional[TaskCard]:
    """Deleta um cartão."""
    card_to_delete = (
        db.query(TaskCard)
        .join(TaskColumn, TaskCard.column_id == TaskColumn.id)
        .filter(
            TaskCard.id == card_id,
            TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not card_to_delete:
        return None
    
    db.delete(card_to_delete)
    db.commit()
    return card_to_delete


def move_task_card(db: Session, card_id: int, new_column_id: int, user_id: UUID) -> Optional[TaskCard]:
    """
    Move um cartão para uma nova coluna.
    
    Returns:
        O cartão movido se sucesso, None se erro
    """
    # Busca o cartão e verifica propriedade
    card_to_move = (
        db.query(TaskCard)
        .join(TaskColumn, TaskCard.column_id == TaskColumn.id)
        .filter(
            TaskCard.id == card_id,
            TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not card_to_move:
        return None

    # Verifica se coluna de destino existe e pertence ao usuário
    destination_column = db.query(TaskColumn).filter(
        TaskColumn.id == new_column_id,
        TaskColumn.owner_id == user_id
    ).first()

    if not destination_column:
        return None

    # Move o cartão
    card_to_move.column_id = new_column_id
    db.commit()
    db.refresh(card_to_move)
    return card_to_move