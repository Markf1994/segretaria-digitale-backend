"""add note column to dispositivi"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_note_to_dispositivo"
down_revision = "0005_optional_times_for_day_off"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("dispositivi") as batch_op:
        batch_op.add_column(sa.Column("note", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("dispositivi") as batch_op:
        batch_op.drop_column("note")
