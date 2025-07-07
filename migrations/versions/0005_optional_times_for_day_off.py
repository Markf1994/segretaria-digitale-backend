"""make inizio_1 and fine_1 nullable"""

from alembic import op
import sqlalchemy as sa

revision = "0005_optional_times_for_day_off"
down_revision = "0004_pdf_file_uuid_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("turni") as batch_op:
        batch_op.alter_column("inizio_1", nullable=True)
        batch_op.alter_column("fine_1", nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("turni") as batch_op:
        batch_op.alter_column("inizio_1", nullable=False)
        batch_op.alter_column("fine_1", nullable=False)
