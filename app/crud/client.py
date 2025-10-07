"""
CRUD de clientes.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.models import Client
from app.schemas import ClientCreate, ClientUpdate


def get_user_clients(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Client]:
    """Lista os clientes de um usuário."""
    return db.query(Client).filter(Client.owner_id == user_id).offset(skip).limit(limit).all()


def get_client_by_id(db: Session, client_id: UUID, user_id: UUID) -> Optional[Client]:
    """Busca um cliente por ID com verificação de propriedade."""
    return db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == user_id
    ).first()


def create_user_client(db: Session, client: ClientCreate, user_id: UUID) -> Client:
    """Cria um novo cliente."""
    client_data = client.model_dump(exclude_unset=True)
    db_client = Client(**client_data, owner_id=user_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: UUID, client_update: ClientUpdate, user_id: UUID) -> Optional[Client]:
    """Atualiza um cliente."""
    db_client = get_client_by_id(db, client_id=client_id, user_id=user_id)
    if not db_client:
        return None
    
    update_data = client_update.model_dump(exclude_unset=True, by_alias=False)
    
    # Handle address separately (JSONB field)
    if 'address' in update_data and update_data['address'] is not None:
        db_client.address = update_data.pop('address')
    
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db_client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: UUID, user_id: UUID) -> Optional[Client]:
    """Deleta um cliente."""
    db_client = get_client_by_id(db, client_id=client_id, user_id=user_id)
    if not db_client:
        return None
    
    db.delete(db_client)
    db.commit()
    return db_client