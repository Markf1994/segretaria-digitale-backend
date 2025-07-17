"""create segnalazioni table"""

from alembic import op
import sqlalchemy as sa

revision = "0008_create_segnalazioni_table"
down_revision = "0007_add_luogo_data_to_horizontal_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "segnalazioni",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("stato", sa.String(), nullable=False),
        sa.Column("priorita", sa.String(), nullable=True),
        sa.Column("data", sa.DateTime(), nullable=False),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("latitudine", sa.Float(), nullable=True),
        sa.Column("longitudine", sa.Float(), nullable=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_index("ix_segnalazioni_id", "segnalazioni", ["id"])


def downgrade() -> None:
    op.drop_index("ix_segnalazioni_id", table_name="segnalazioni")
    op.drop_table("segnalazioni")
