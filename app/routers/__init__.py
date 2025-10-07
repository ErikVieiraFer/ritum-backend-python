"""
Routers da API - endpoints organizados por domínio.
"""

from app.routers import (
    auth,
    users,
    clients,
    processes,
    kanban,
    ai,
    extrajudicial,
    documents,
)

__all__ = [
    "auth",
    "users",
    "clients",
    "processes",
    "kanban",
    "ai",
    "extrajudicial",
    "documents",
]