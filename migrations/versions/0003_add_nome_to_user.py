"""add nome to user"""

from alembic import op
import sqlalchemy as sa

revision = '0003_add_nome_to_user'
down_revision = '0002_create_turni_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('nome', sa.String(), nullable=False, server_default=''))
    op.execute(
        """
        UPDATE users
        SET nome = CASE
            WHEN email = 'marco@comune.castione.bg.it' THEN 'Ag.Sc. Fenaroli Marco'
            WHEN email = 'rossella@comune.castione.bg.it' THEN 'Sovr. Licini Rossella'
            WHEN email = 'mattia@comune.castione.bg.it' THEN 'Ag.Sc. Danesi Mattia'
            ELSE nome
        END
        """
    )


def downgrade() -> None:
    op.drop_column('users', 'nome')
