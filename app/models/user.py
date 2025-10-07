"""
Modelo de Usuário (advogados).
"""

import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    oab_number = Column(String, nullable=True)
    oab_state = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    address = Column(JSONB, nullable=True)
    phone = Column(String, nullable=True)
    
    # Relacionamentos
    processes = relationship("Process", back_populates="owner", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="owner", cascade="all, delete-orphan")
    task_columns = relationship("TaskColumn", back_populates="owner", cascade="all, delete-orphan")
    extrajudicial_cases = relationship("ExtrajudicialCase", back_populates="owner", cascade="all, delete-orphan")
    intimations = relationship("Intimation", back_populates="owner", cascade="all, delete-orphan")