"""add luogo and data to segnaletica_orizzontale_items"""

from alembic import op
import sqlalchemy as sa

revision = "0007_add_luogo_data_to_horizontal_items"
down_revision = "0006_inventory_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("segnaletica_orizzontale_items") as batch_op:
        batch_op.add_column(sa.Column("luogo", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("data", sa.Date(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("segnaletica_orizzontale_items") as batch_op:
        batch_op.drop_column("data")
        batch_op.drop_column("luogo")
