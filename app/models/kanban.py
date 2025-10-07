"""
Modelos do quadro Kanban (colunas e cartões).
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TaskColumn(Base):
    __tablename__ = "task_columns"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="task_columns")
    
    cards = relationship("TaskCard", cascade="all, delete-orphan", backref="column")


class TaskCard(Base):
    __tablename__ = "task_cards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    column_id = Column(Integer, ForeignKey("task_columns.id"), nullable=False)