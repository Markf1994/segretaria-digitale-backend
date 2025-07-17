"""add tipo quantita luogo columns"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_fields_to_segnaletica_verticale"
down_revision = "0005_optional_times_for_day_off"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "segnaletica_verticale",
        sa.Column("tipo", sa.String(), nullable=True),
    )
    op.add_column(
        "segnaletica_verticale",
        sa.Column("quantita", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "segnaletica_verticale",
        sa.Column("luogo", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("segnaletica_verticale", "luogo")
    op.drop_column("segnaletica_verticale", "quantita")
    op.drop_column("segnaletica_verticale", "tipo")
