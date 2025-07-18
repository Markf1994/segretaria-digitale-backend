"""create segnaletica orizzontale table"""

from alembic import op
import sqlalchemy as sa

revision = "0010_create_segnaletica_orizzontale"
down_revision = "0009_update_segnalazioni_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "segnaletica_orizzontale",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("azienda", sa.String(), nullable=False),
        sa.Column("anno", sa.Integer(), nullable=False),
        sa.Column("descrizione", sa.String(), nullable=False),
    )
    op.create_index(
        "ix_segnaletica_orizzontale_id", "segnaletica_orizzontale", ["id"]
    )


def downgrade() -> None:
    op.drop_index("ix_segnaletica_orizzontale_id", table_name="segnaletica_orizzontale")
    op.drop_table("segnaletica_orizzontale")
