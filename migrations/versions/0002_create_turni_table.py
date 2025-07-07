"""create turni table"""

from alembic import op
import sqlalchemy as sa

revision = "0002_create_turni_table"
down_revision = "0001_create_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "turni",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("giorno", sa.Date(), nullable=False),
        sa.Column("inizio_1", sa.Time(), nullable=False),
        sa.Column("fine_1", sa.Time(), nullable=False),
        sa.Column("inizio_2", sa.Time(), nullable=True),
        sa.Column("fine_2", sa.Time(), nullable=True),
        sa.Column("inizio_3", sa.Time(), nullable=True),
        sa.Column("fine_3", sa.Time(), nullable=True),
        sa.Column("tipo", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
    )
    op.create_index("ix_turni_id", "turni", ["id"])


def downgrade() -> None:
    op.drop_index("ix_turni_id", table_name="turni")
    op.drop_table("turni")
