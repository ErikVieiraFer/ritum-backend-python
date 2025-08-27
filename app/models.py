# ritum-backend/app/models.py

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .database import Base

# --- MODELO DE USUÁRIO ---
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Changed to UUID
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

# --- MODELO DE CLIENTE ---
class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Changed to UUID
    full_name = Column(String, index=True) # Changed from 'name' to 'full_name'
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    cpf = Column(String, unique=True, index=True, nullable=True)
    rg = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    profession = Column(String, nullable=True)
    address = Column(JSONB, nullable=True) # Added address as JSONB
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Changed to UUID
    owner = relationship("User", back_populates="clients")

# --- MODELOS DE PROCESSO E ANDAMENTOS ---
class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True)
    number = Column(String, index=True, unique=True, nullable=False) 
    client_name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="Ativo")
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Changed to UUID
    owner = relationship("User", back_populates="processes")

    updates = relationship("ProcessUpdate", back_populates="process", cascade="all, delete-orphan")

class ProcessUpdate(Base):
    __tablename__ = "process_updates"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)

    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    process = relationship("Process", back_populates="updates")

# --- MODELOS DO KANBAN ---
class TaskColumn(Base):
    __tablename__ = "task_columns"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Changed to UUID
    owner = relationship("User", back_populates="task_columns")
    
    cards = relationship("TaskCard", cascade="all, delete-orphan", backref="column")

class TaskCard(Base):
    __tablename__ = "task_cards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    column_id = Column(Integer, ForeignKey("task_columns.id"), nullable=False)

# --- MODELO DE CASOS EXTRAJUDICIAIS ---
class ExtrajudicialCase(Base):
    __tablename__ = "extrajudicial_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Changed to UUID
    case_type = Column(String, nullable=False)
    case_name = Column(String, nullable=False)
    status = Column(String, default="InProgress")
    data = Column(JSONB, nullable=True, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="extrajudicial_cases")

# --- MODELO DE BUSCA DE JURISPRUDÊNCIA ---
class JurisprudenceDocument(Base):
    __tablename__ = "jurisprudence_documents"

    id = Column(Integer, primary_key=True, index=True)
    court = Column(String, nullable=False, index=True)
    case_number = Column(String, nullable=False, index=True)
    publication_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)