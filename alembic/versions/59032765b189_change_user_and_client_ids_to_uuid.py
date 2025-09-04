"""Change user and client IDs to UUID

Revision ID: 59032765b189
Revises: b7d0317fd72d
Create Date: 2025-09-03 19:48:36.771605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59032765b189'
down_revision: Union[str, Sequence[str], None] = 'b7d0317fd72d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable the uuid-ossp extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Alter columns, now also removing the old server_default for PKs
    op.alter_column('clients', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               server_default=None, # Remove old default
               postgresql_using='uuid_generate_v4()')
    op.alter_column('clients', 'owner_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               postgresql_using='uuid_generate_v4()')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.alter_column('extrajudicial_cases', 'owner_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               postgresql_using='uuid_generate_v4()')
    op.alter_column('processes', 'owner_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               postgresql_using='uuid_generate_v4()')
    op.alter_column('task_columns', 'owner_id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               postgresql_using='uuid_generate_v4()')
    op.alter_column('users', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.UUID(as_uuid=True),
               existing_nullable=False,
               server_default=None, # Remove old default
               postgresql_using='uuid_generate_v4()')
    op.drop_index(op.f('ix_users_id'), table_name='users')


def downgrade() -> None:
    """Downgrade schema."""
    # Downgrade path is complex and not implemented for this migration.
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    pass
