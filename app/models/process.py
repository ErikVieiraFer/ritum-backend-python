"""
Modelos de Processo e Andamentos.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True)
    number = Column(String, index=True, unique=True, nullable=False)
    client_name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="Ativo")
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="processes")

    updates = relationship("ProcessUpdate", back_populates="process", cascade="all, delete-orphan")


class ProcessUpdate(Base):
    __tablename__ = "process_updates"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)

    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    process = relationship("Process", back_populates="updates")