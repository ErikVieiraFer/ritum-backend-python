"""
SQLAlchemy models para o banco de dados.
"""

from app.models.user import User
from app.models.client import Client
from app.models.process import Process, ProcessUpdate
from app.models.kanban import TaskColumn, TaskCard
from app.models.extrajudicial import (
    ExtrajudicialCase,
    JurisprudenceDocument,
    Intimation
)

__all__ = [
    "User",
    "Client",
    "Process",
    "ProcessUpdate",
    "TaskColumn",
    "TaskCard",
    "ExtrajudicialCase",
    "JurisprudenceDocument",
    "Intimation",
]