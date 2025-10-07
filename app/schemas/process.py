"""
Schemas de processo.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ProcessUpdateBase(BaseModel):
    date: datetime
    description: str


class ProcessUpdateCreate(ProcessUpdateBase):
    pass


class ProcessUpdate(ProcessUpdateBase):
    id: int
    process_id: int
    model_config = ConfigDict(from_attributes=True)


class ProcessBase(BaseModel):
    number: str
    client_name: str
    type: str
    status: Optional[str] = "Ativo"


class ProcessCreate(ProcessBase):
    pass


class Process(ProcessBase):
    id: int
    owner_id: UUID
    updates: List[ProcessUpdate] = []
    model_config = ConfigDict(from_attributes=True)