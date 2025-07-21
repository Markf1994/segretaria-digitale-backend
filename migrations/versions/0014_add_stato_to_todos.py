"""add stato column to todos"""

from alembic import op
import sqlalchemy as sa
from app.schemas.todo import StatoToDo

revision = "0014_add_stato_to_todos"
down_revision = "0013_remove_horizontal_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "todos",
        sa.Column(
            "stato",
            sa.String(length=30),
            nullable=False,
            server_default=StatoToDo.ATTIVO.value,
        ),
    )


def downgrade() -> None:
    op.drop_column("todos", "stato")
