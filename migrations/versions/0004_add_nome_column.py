"""add nome column to users"""

from alembic import op
import sqlalchemy as sa

revision = '0004_add_nome_column'
down_revision = '0003_add_nome_to_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('nome', sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'nome')
