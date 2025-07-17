"""create segnalazioni table"""

from alembic import op
import sqlalchemy as sa
from app.schemas.segnalazione import TipoSegnalazione, StatoSegnalazione

revision = "0008_create_segnalazioni_table"
down_revision = "0007_add_luogo_data_to_horizontal_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "segnalazioni",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "tipo", sa.Enum(TipoSegnalazione, name="tipo_segnalazione"), nullable=False
        ),
        sa.Column(
            "stato",
            sa.Enum(StatoSegnalazione, name="stato_segnalazione"),
            nullable=False,
        ),
        sa.Column("priorita", sa.Integer(), nullable=True),
        sa.Column("data_segnalazione", sa.DateTime(), nullable=False),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("latitudine", sa.Float(), nullable=True),
        sa.Column("longitudine", sa.Float(), nullable=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_index("ix_segnalazioni_id", "segnalazioni", ["id"])


def downgrade() -> None:
    op.drop_index("ix_segnalazioni_id", table_name="segnalazioni")
    op.drop_table("segnalazioni")
    sa.Enum(TipoSegnalazione, name="tipo_segnalazione").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum(StatoSegnalazione, name="stato_segnalazione").drop(
        op.get_bind(), checkfirst=True
    )
