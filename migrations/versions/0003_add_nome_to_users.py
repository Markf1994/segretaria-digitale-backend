"""add nome column to users"""

from alembic import op
import sqlalchemy as sa

revision = '0003_add_nome_to_users'
down_revision = '0002_create_turni_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('nome', sa.String(), nullable=False, server_default=''))
    op.alter_column('users', 'nome', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'nome')
