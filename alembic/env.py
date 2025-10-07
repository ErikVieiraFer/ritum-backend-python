"""
Alembic environment configuration.
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adicionar pasta pai ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importar Base e models
from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models import (
    User, Client, Process, ProcessUpdate,
    TaskColumn, TaskCard,
    ExtrajudicialCase, JurisprudenceDocument, Intimation
)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata

# Configurar URL do banco
config.set_main_option("sqlalchemy.url", str(SQLALCHEMY_DATABASE_URL))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=str(SQLALCHEMY_DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = str(SQLALCHEMY_DATABASE_URL)
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()