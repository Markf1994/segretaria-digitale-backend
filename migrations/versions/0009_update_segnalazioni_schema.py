"""update segnalazioni schema"""

from alembic import op
import sqlalchemy as sa
from app.schemas.segnalazione import TipoSegnalazione, StatoSegnalazione

revision = "0009_update_segnalazioni_schema"
down_revision = "0008_create_segnalazioni_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("segnalazioni") as batch_op:
        batch_op.alter_column("priorita", type_=sa.Integer())
        batch_op.alter_column("data", new_column_name="data_segnalazione")
        batch_op.alter_column(
            "tipo",
            type_=sa.Enum(TipoSegnalazione, name="tipo_segnalazione"),
        )
        batch_op.alter_column(
            "stato",
            type_=sa.Enum(StatoSegnalazione, name="stato_segnalazione"),
        )


def downgrade() -> None:
    with op.batch_alter_table("segnalazioni") as batch_op:
        batch_op.alter_column(
            "stato",
            type_=sa.String(),
        )
        batch_op.alter_column(
            "tipo",
            type_=sa.String(),
        )
        batch_op.alter_column("data_segnalazione", new_column_name="data")
        batch_op.alter_column("priorita", type_=sa.String())

