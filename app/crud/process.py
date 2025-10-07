"""
CRUD de processos.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.models import Process
from app.schemas import ProcessCreate


def get_user_processes(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Process]:
    """Lista os processos de um usuário."""
    return db.query(Process).filter(Process.owner_id == user_id).offset(skip).limit(limit).all()


def create_user_process(db: Session, process: ProcessCreate, user_id: UUID) -> Process:
    """Cria um novo processo."""
    db_process = Process(**process.model_dump(), owner_id=user_id)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process