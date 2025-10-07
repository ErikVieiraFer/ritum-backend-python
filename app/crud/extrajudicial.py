"""
CRUD de casos extrajudiciais e intimações.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime
from typing import Optional

from app.models import ExtrajudicialCase, Intimation
from app.schemas import CaseCreateRequest, CaseUpdateRequest


def create_extrajudicial_case(db: Session, case: CaseCreateRequest, user_id: UUID) -> ExtrajudicialCase:
    """Cria um novo caso extrajudicial."""
    db_case = ExtrajudicialCase(
        **case.model_dump(),
        owner_id=user_id,
        data={}
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def get_extrajudicial_case(db: Session, case_id: UUID, user_id: UUID) -> Optional[ExtrajudicialCase]:
    """Busca um caso extrajudicial por ID."""
    return db.query(ExtrajudicialCase).filter(
        ExtrajudicialCase.id == case_id,
        ExtrajudicialCase.owner_id == user_id
    ).first()


def update_extrajudicial_case(db: Session, case_id: UUID, case_data: CaseUpdateRequest, user_id: UUID) -> Optional[ExtrajudicialCase]:
    """Atualiza o campo data de um caso extrajudicial."""
    db_case = get_extrajudicial_case(db, case_id=case_id, user_id=user_id)
    
    if not db_case:
        return None
    
    db_case.data = case_data.data
    db.commit()
    db.refresh(db_case)
    return db_case


def get_intimations_stats(db: Session, user_id: UUID, start_date: date, end_date: date) -> int:
    """Conta intimações de um usuário em um intervalo de datas."""
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    count = (
        db.query(Intimation)
        .filter(
            Intimation.owner_id == user_id,
            Intimation.publication_date >= start_datetime,
            Intimation.publication_date <= end_datetime,
        )
        .count()
    )
    return count