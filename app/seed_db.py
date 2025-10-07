"""
Script para popular o banco de dados com dados de teste.
Útil para desenvolvimento e testes.

Uso:
    python seed_db.py
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, User, Client, Process, TaskColumn, TaskCard
from app.core.security import get_password_hash


def create_tables():
    """Cria todas as tabelas no banco de dados."""
    print("📦 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")


def seed_users(db: Session):
    """Cria usuários de teste."""
    print("\n👤 Criando usuários de teste...")
    
    # Verificar se já existem usuários
    existing_user = db.query(User).filter(User.email == "advogado@ritum.io").first()
    if existing_user:
        print("⚠️  Usuários já existem. Pulando...")
        return existing_user
    
    # Criar usuário de teste
    test_user = User(
        name="Dr. João Silva",
        email="advogado@ritum.io",
        hashed_password=get_password_hash("senha123"),
        oab_number="123456",
        oab_state="SP",
        cpf="123.456.789-00",
        phone="(11) 98765-4321",
        address={
            "street": "Rua dos Advogados",
            "number": "100",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01000-000"
        }
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"✅ Usuário criado: {test_user.email} (senha: senha123)")
    return test_user


def seed_clients(db: Session, user: User):
    """Cria clientes de teste."""
    print("\n👥 Criando clientes de teste...")
    
    clients_data = [
        {
            "full_name": "Maria Santos",
            "email": "maria.santos@email.com",
            "phone": "(11) 91234-5678",
            "cpf": "987.654.321-00",
            "rg": "12.345.678-9",
            "nationality": "Brasileira",
            "marital_status": "Casada",
            "profession": "Empresária",
        },
        {
            "full_name": "Pedro Oliveira",
            "email": "pedro.oliveira@email.com",
            "phone": "(11) 99876-5432",
            "cpf": "111.222.333-44",
            "rg": "98.765.432-1",
            "nationality": "Brasileiro",
            "marital_status": "Solteiro",
            "profession": "Engenheiro",
        },
        {
            "full_name": "Ana Costa",
            "email": "ana.costa@email.com",
            "phone": "(11) 97777-8888",
            "cpf": "555.666.777-88",
            "nationality": "Brasileira",
            "marital_status": "Divorciada",
            "profession": "Médica",
        }
    ]
    
    for client_data in clients_data:
        client = Client(**client_data, owner_id=user.id)
        db.add(client)
    
    db.commit()
    print(f"✅ {len(clients_data)} clientes criados!")


def seed_processes(db: Session, user: User):
    """Cria processos de teste."""
    print("\n📁 Criando processos de teste...")
    
    processes_data = [
        {
            "number": "1000550-94.2023.8.26.0100",
            "client_name": "Maria Santos",
            "type": "Ação de Cobrança",
            "status": "Ativo",
        },
        {
            "number": "2000123-45.2023.8.26.0001",
            "client_name": "Pedro Oliveira",
            "type": "Ação de Despejo",
            "status": "Ativo",
        },
        {
            "number": "3000789-12.2023.8.26.0555",
            "client_name": "Ana Costa",
            "type": "Divórcio Consensual",
            "status": "Concluído",
        }
    ]
    
    for process_data in processes_data:
        process = Process(**process_data, owner_id=user.id)
        db.add(process)
    
    db.commit()
    print(f"✅ {len(processes_data)} processos criados!")


def seed_kanban(db: Session, user: User):
    """Cria quadro Kanban de teste."""
    print("\n📋 Criando quadro Kanban de teste...")
    
    # Criar colunas
    columns_data = [
        {"title": "A Fazer", "position": 0},
        {"title": "Em Andamento", "position": 1},
        {"title": "Aguardando", "position": 2},
        {"title": "Concluído", "position": 3},
    ]
    
    columns = []
    for col_data in columns_data:
        column = TaskColumn(**col_data, owner_id=user.id)
        db.add(column)
        db.flush()  # Para obter o ID
        columns.append(column)
    
    # Criar cartões
    cards_data = [
        {
            "title": "Protocolar Petição Inicial - Processo Maria Santos",
            "description": "Processo 1000550-94.2023.8.26.0100",
            "due_date": datetime.now() + timedelta(days=3),
            "column_id": columns[0].id,
        },
        {
            "title": "Preparar Contestação - Pedro Oliveira",
            "description": "Prazo: 15 dias",
            "due_date": datetime.now() + timedelta(days=7),
            "column_id": columns[1].id,
        },
        {
            "title": "Aguardar Decisão Liminar",
            "description": "Processo em análise pelo juiz",
            "due_date": datetime.now() + timedelta(days=15),
            "column_id": columns[2].id,
        },
        {
            "title": "Divórcio Ana Costa - Finalizado",
            "description": "Processo concluído com sucesso",
            "due_date": datetime.now() - timedelta(days=5),
            "column_id": columns[3].id,
        }
    ]
    
    for card_data in cards_data:
        card = TaskCard(**card_data)
        db.add(card)
    
    db.commit()
    print(f"✅ {len(columns)} colunas e {len(cards_data)} cartões criados!")


def main():
    """Função principal do script."""
    print("=" * 60)
    print("🌱 SEED DATABASE - Ritum")
    print("=" * 60)
    
    try:
        # Criar tabelas
        create_tables()
        
        # Criar sessão
        db = SessionLocal()
        
        try:
            # Popular banco de dados
            user = seed_users(db)
            seed_clients(db, user)
            seed_processes(db, user)
            seed_kanban(db, user)
            
            print("\n" + "=" * 60)
            print("✅ Banco de dados populado com sucesso!")
            print("=" * 60)
            print("\n📝 CREDENCIAIS DE TESTE:")
            print("   Email: advogado@ritum.io")
            print("   Senha: senha123")
            print("\n🔗 Acesse: http://localhost:8000/docs")
            print("=" * 60)
            
        finally:
            db.close()
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()