from sqlalchemy.orm import Session, selectinload
from . import models, schemas, security
from uuid import UUID
from sqlalchemy import or_, and_
from datetime import date, datetime
from typing import List, Optional

def get_user_by_email(db: Session, email: str):
    """Busca um usuário pelo seu endereço de email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário no banco de dados com senha criptografada."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, name=user.name, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Autentica um usuário, verificando email e senha."""
    user = get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_id(db: Session, user_id: UUID):
    """Busca um usuário pelo seu ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user_profile(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
    """
    Atualiza o perfil de um usuário.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    # Handle address separately as it's a nested JSONB field
    if 'address' in update_data and update_data['address'] is not None:
        db_user.address = update_data.pop('address')

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.User, password_update: schemas.UserPasswordUpdate):
    """
    Atualiza a senha do usuário após verificar a senha atual.
    """
    if not security.verify_password(password_update.current_password, user.hashed_password):
        return False

    hashed_password = security.get_password_hash(password_update.new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return True

# --- Funções de Cliente ---
def get_user_clients(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """Lista os clientes de um usuário específico."""
    return db.query(models.Client).filter(models.Client.owner_id == user_id).offset(skip).limit(limit).all()

def get_client_by_id(db: Session, client_id: UUID, user_id: UUID):
    """Busca um cliente por ID, com a verificação de propriedade."""
    return db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.owner_id == user_id
    ).first()

def create_user_client(db: Session, client: schemas.ClientCreate, user_id: UUID):
    """Cria um novo cliente para um usuário."""
    client_data = client.model_dump(exclude_unset=True) # Use exclude_unset to only include provided fields
    
    # Pydantic já converte AddressSchema para dict, então podemos passar diretamente
    # para o modelo SQLAlchemy que espera JSONB
    db_client = models.Client(**client_data, owner_id=user_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: UUID, client_update: schemas.ClientUpdate, user_id: UUID):
    """Encontra e atualiza um cliente, lidando com os dados Optional."""
    db_client = get_client_by_id(db, client_id=client_id, user_id=user_id)
    if not db_client:
        return None
    
    update_data = client_update.model_dump(exclude_unset=True, by_alias=False) # Use original field names
    
    # Handle address separately as it's a nested JSONB field
    if 'address' in update_data and update_data['address'] is not None:
        db_client.address = update_data.pop('address') # Update address and remove from update_data
    
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db_client.updated_at = datetime.utcnow() # Update updated_at timestamp
    db.commit()
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: UUID, user_id: UUID):
    """Deleta um cliente, com a verificação de propriedade."""
    db_client = get_client_by_id(db, client_id=client_id, user_id=user_id)
    if not db_client:
        return None
    
    db.delete(db_client)
    db.commit()
    return db_client

# --- Funções de Processo ---
def get_user_processes(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """Lista os processos de um usuário específico."""
    return db.query(models.Process).filter(models.Process.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_process(db: Session, process: schemas.ProcessCreate, user_id: UUID):
    """Cria um novo processo para um usuário."""
    db_process = models.Process(**process.model_dump(), owner_id=user_id)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process

# --- Funções do Kanban ---
def get_board_for_user(db: Session, user_id: UUID):
    """
    Busca todas as colunas e seus respectivos cartões para um usuário específico.
    Usa selectinload para otimizar o carregamento dos cartões (evita N+1 queries).
    """
    return (
        db.query(models.TaskColumn)
        .filter(models.TaskColumn.owner_id == user_id)
        .order_by(models.TaskColumn.position)
        .options(selectinload(models.TaskColumn.cards))
        .all()
    )

def create_task_column(db: Session, column: schemas.TaskColumnCreate, user_id: UUID):
    """
    Cria uma nova coluna no quadro Kanban para um usuário."""
    db_column = models.TaskColumn(
        **column.model_dump(),
        owner_id=user_id
    )
    db.add(db_column)
    db.commit()
    db.refresh(db_column)
    return db_column

def create_task_card(db: Session, card: schemas.TaskCardCreate, column_id: int, user_id: UUID):
    """
    Cria um novo cartão em uma coluna, após verificar a permissão do usuário."""

    db_column = db.query(models.TaskColumn).filter(
        models.TaskColumn.id == column_id,
        models.TaskColumn.owner_id == user_id
    ).first()

    if not db_column:
        return None

    db_card = models.TaskCard(
        **card.model_dump(),
        column_id=column_id
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def move_task_card(db: Session, card_id: int, new_column_id: int, user_id: UUID):
    """
    Move um cartão para uma nova coluna, realizando verificações de permissão.
    """
    # Passo 1: Encontra o cartão e verifica se ele pertence ao usuário (via join com a coluna)
    card_to_move = (
        db.query(models.TaskCard)
        .join(models.TaskColumn, models.TaskCard.column_id == models.TaskColumn.id)
        .filter(
            models.TaskCard.id == card_id,
            models.TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not card_to_move:
        # Cartão não encontrado ou não pertence ao usuário
        return {"ok": False, "error": "Card not found or permission denied"}

    # Passo 2: Verifica se a coluna de destino existe e pertence ao mesmo usuário
    destination_column = db.query(models.TaskColumn).filter(
        models.TaskColumn.id == new_column_id,
        models.TaskColumn.owner_id == user_id
    ).first()

    if not destination_column:
        # Coluna de destino não encontrada ou não pertence ao usuário
        return {"ok": False, "error": "Destination column not found or permission denied"}

    # Passo 3: Se tudo estiver ok, atualiza a coluna do cartão
    card_to_move.column_id = new_column_id
    db.commit()
    db.refresh(card_to_move)

    return {"ok": True, "card": card_to_move}

def delete_task_card(db: Session, card_id: int, user_id: UUID):
    """
    Deleta um cartão, verificando a permissão do usuário.
    """
    
    # Encontra o cartão e verifica se ele pertence ao usuário (via join com a coluna)
    card_to_delete = (
        db.query(models.TaskCard)
        .join(models.TaskColumn, models.TaskCard.column_id == models.TaskColumn.id)
        .filter(
            models.TaskCard.id == card_id,
            models.TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not card_to_delete:
        # Cartão não encontrado ou não pertence ao usuário
        return None
    
    db.delete(card_to_delete)
    db.commit()
    
    return card_to_delete

def delete_task_column(db: Session, column_id: int, user_id: UUID):
    """
    Deleta uma coluna, verificando a permissão do usuário.
    """
    
    # Encontra a coluna e verifica se ela pertence ao usuário logado
    column_to_delete = db.query(models.TaskColumn).filter(
        models.TaskColumn.id == column_id,
        models.TaskColumn.owner_id == user_id
    ).first()

    if not column_to_delete:
        # Coluna não encontrada ou não pertence ao usuário
        return None
    
    db.delete(column_to_delete)
    db.commit()
    
    return column_to_delete

def update_task_column(db: Session, column_id: int, column_update: schemas.TaskColumnUpdate, user_id: UUID):
    """
    Atualiza o título de uma coluna, verificando a permissão do usuário.
    """
    
    db_column = db.query(models.TaskColumn).filter(
        models.TaskColumn.id == column_id,
        models.TaskColumn.owner_id == user_id
    ).first()

    if not db_column:
        return None

    db_column.title = column_update.title
    db.commit()
    db.refresh(db_column)
    
    return db_column

def update_task_card(db: Session, card_id: int, card_update: schemas.TaskCardUpdate, user_id: UUID):
    """
    Atualiza os detalhes de um cartão, verificando a permissão do usuário.
    """
    
    db_card = (
        db.query(models.TaskCard)
        .join(models.TaskColumn, models.TaskCard.column_id == models.TaskColumn.id)
        .filter(
            models.TaskCard.id == card_id,
            models.TaskColumn.owner_id == user_id
        )
        .first()
    )

    if not db_card:
        return None
    
    # Pega os dados do Pydantic model como um dict
    update_data = card_update.model_dump(exclude_unset=True)
    
    # Atualiza apenas os campos que foram enviados
    for key, value in update_data.items():
        setattr(db_card, key, value)
        
    db.commit()
    db.refresh(db_card)
    
    return db_card

# --- Funções de Casos Extrajudiciais ---

def create_extrajudicial_case(db: Session, case: schemas.CaseCreateRequest, user_id: UUID):
    """
    Cria um novo caso extrajudicial para um usuário com um campo de dados vazio."""
    db_case = models.ExtrajudicialCase(
        **case.model_dump(),
        owner_id=user_id,
        data={}
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def get_extrajudicial_case(db: Session, case_id: UUID, user_id: UUID):
    """
    Busca um caso extrajudicial específico pelo ID, garantindo que pertença ao usuário."""
    return db.query(models.ExtrajudicialCase).filter(
        models.ExtrajudicialCase.id == case_id, 
        models.ExtrajudicialCase.owner_id == user_id
    ).first()

def update_extrajudicial_case(db: Session, case_id: UUID, case_data: schemas.CaseUpdateRequest, user_id: UUID):
    """
    Atualiza o campo de dados de um caso extrajudicial, verificando a propriedade."""
    db_case = get_extrajudicial_case(db, case_id=case_id, user_id=user_id)
    
    if not db_case:
        return None
        
    # Como o schema agora usa Dict[str, Any], podemos atribuir diretamente.
    # O SQLAlchemy detecta a mudança no dicionário "mutável" e persiste.
    db_case.data = case_data.data
    
    db.commit()
    db.refresh(db_case)
    return db_case

# --- Funções de Busca de Jurisprudência ---
def search_jurisprudence_documents(
    db: Session,
    query: str,
    courts: Optional[List[str]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 10
):
    """
    Busca documentos de jurisprudência com base em um termo de busca e filtros opcionais.
    """
    # Constrói a query base
    db_query = db.query(models.JurisprudenceDocument)

    # Filtra por termo de busca (case_number, summary, full_text)
    if query:
        db_query = db_query.filter(
            or_(
                models.JurisprudenceDocument.case_number.ilike(f"%{query}%"),
                models.JurisprudenceDocument.summary.ilike(f"%{query}%"),
                models.JurisprudenceDocument.full_text.ilike(f"%{query}%")
            )
        )

    # Filtra por tribunais
    if courts:
        db_query = db_query.filter(models.JurisprudenceDocument.court.in_(courts))

    # Filtra por data de publicação
    if start_date and end_date:
        db_query = db_query.filter(
            and_(
                models.JurisprudenceDocument.publication_date >= start_date,
                models.JurisprudenceDocument.publication_date <= end_date
            )
        )
    elif start_date:
        db_query = db_query.filter(models.JurisprudenceDocument.publication_date >= start_date)
    elif end_date:
        db_query = db_query.filter(models.JurisprudenceDocument.publication_date <= end_date)

    # Aplica paginação e retorna os resultados
    return db_query.offset(skip).limit(limit).all()

# --- Funções de Intimações ---
def get_intimations_stats(db: Session, user_id: UUID, start_date: date, end_date: date) -> int:
    """Conta o número de intimações para um usuário dentro de um intervalo de datas."""
    # Converte as datas para datetime para corresponder ao tipo do modelo (DateTime)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    count = (
        db.query(models.Intimation)
        .filter(
            models.Intimation.owner_id == user_id,
            models.Intimation.publication_date >= start_datetime,
            models.Intimation.publication_date <= end_datetime,
        )
        .count()
    )
    return count