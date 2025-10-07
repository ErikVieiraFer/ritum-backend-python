"""
Pydantic schemas para validação de dados da API.
"""

from app.schemas.auth import Token, TokenResponse, TokenData
from app.schemas.user import (
    UserBase, UserCreate, User, UserUpdate, UserPasswordUpdate
)
from app.schemas.client import (
    AddressSchema, ClientBase, ClientCreate, ClientUpdate, Client
)
from app.schemas.process import (
    ProcessBase, ProcessCreate, Process,
    ProcessUpdateBase, ProcessUpdateCreate, ProcessUpdate
)
from app.schemas.kanban import (
    TaskCardBase, TaskCardCreate, TaskCard, TaskCardUpdate, TaskCardMove,
    TaskColumnBase, TaskColumnCreate, TaskColumn, TaskColumnUpdate, TaskColumnWithCards
)
from app.schemas.extrajudicial import (
    PersonSchema, AssetSchema, DebtSchema, ChildSchema,
    CaseCreateRequest, CaseUpdateRequest, CaseResponse
)
from app.schemas.ai import (
    PromptGenerationRequest, PromptGenerationResponse,
    PetitionGenerationRequest, PetitionGenerationResponse,
    JurisprudenceSearchRequest, DataJudResult, DataJudSearchResponse
)
from app.schemas.document import (
    ClientDataForDoc, CaseDetailsSchema,
    GenerateDocumentRequest, GenerateDocumentResponse
)

__all__ = [
    # Auth
    "Token", "TokenResponse", "TokenData",
    # User
    "UserBase", "UserCreate", "User", "UserUpdate", "UserPasswordUpdate",
    # Client
    "AddressSchema", "ClientBase", "ClientCreate", "ClientUpdate", "Client",
    # Process
    "ProcessBase", "ProcessCreate", "Process",
    "ProcessUpdateBase", "ProcessUpdateCreate", "ProcessUpdate",
    # Kanban
    "TaskCardBase", "TaskCardCreate", "TaskCard", "TaskCardUpdate", "TaskCardMove",
    "TaskColumnBase", "TaskColumnCreate", "TaskColumn", "TaskColumnUpdate", "TaskColumnWithCards",
    # Extrajudicial
    "PersonSchema", "AssetSchema", "DebtSchema", "ChildSchema",
    "CaseCreateRequest", "CaseUpdateRequest", "CaseResponse",
    # AI
    "PromptGenerationRequest", "PromptGenerationResponse",
    "PetitionGenerationRequest", "PetitionGenerationResponse",
    "JurisprudenceSearchRequest", "DataJudResult", "DataJudSearchResponse",
    # Documents
    "ClientDataForDoc", "CaseDetailsSchema",
    "GenerateDocumentRequest", "GenerateDocumentResponse",
]