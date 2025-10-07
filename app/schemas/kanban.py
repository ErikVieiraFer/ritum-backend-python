"""
Schemas do quadro Kanban.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class TaskCardBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCardCreate(TaskCardBase):
    pass


class TaskCard(TaskCardBase):
    id: int
    column_id: int
    model_config = ConfigDict(from_attributes=True)


class TaskCardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCardMove(BaseModel):
    new_column_id: int


class TaskColumnBase(BaseModel):
    title: str
    position: int


class TaskColumnCreate(TaskColumnBase):
    pass


class TaskColumn(TaskColumnBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TaskColumnWithCards(TaskColumn):
    cards: List[TaskCard] = []


class TaskColumnUpdate(BaseModel):
    title: str