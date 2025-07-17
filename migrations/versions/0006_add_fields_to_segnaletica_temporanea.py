"""add luogo fine_validita quantita to segnaletica_temporanea"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_fields_to_segnaletica_temporanea"
down_revision = "0005_optional_times_for_day_off"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("segnaletica_temporanea") as batch_op:
        batch_op.add_column(sa.Column("luogo", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("fine_validita", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("quantita", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("segnaletica_temporanea") as batch_op:
        batch_op.drop_column("quantita")
        batch_op.drop_column("fine_validita")
        batch_op.drop_column("luogo")
