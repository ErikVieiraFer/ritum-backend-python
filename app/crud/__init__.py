"""
CRUD operations para todas as entidades.
"""

from app.crud.user import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    authenticate_user,
    update_user_profile,
    update_user_password,
)
from app.crud.client import (
    get_user_clients,
    get_client_by_id,
    create_user_client,
    update_client,
    delete_client,
)
from app.crud.process import (
    get_user_processes,
    create_user_process,
)
from app.crud.kanban import (
    get_board_for_user,
    create_task_column,
    update_task_column,
    delete_task_column,
    create_task_card,
    update_task_card,
    delete_task_card,
    move_task_card,
)
from app.crud.extrajudicial import (
    create_extrajudicial_case,
    get_extrajudicial_case,
    update_extrajudicial_case,
    get_intimations_stats,
)

__all__ = [
    # User
    "get_user_by_email",
    "get_user_by_id",
    "create_user",
    "authenticate_user",
    "update_user_profile",
    "update_user_password",
    # Client
    "get_user_clients",
    "get_client_by_id",
    "create_user_client",
    "update_client",
    "delete_client",
    # Process
    "get_user_processes",
    "create_user_process",
    # Kanban
    "get_board_for_user",
    "create_task_column",
    "update_task_column",
    "delete_task_column",
    "create_task_card",
    "update_task_card",
    "delete_task_card",
    "move_task_card",
    # Extrajudicial
    "create_extrajudicial_case",
    "get_extrajudicial_case",
    "update_extrajudicial_case",
    "get_intimations_stats",
]