"""update segnalazioni stato check constraint"""

from alembic import op

revision = "0011_update_segnalazioni_stato_check"
down_revision = "0010_create_segnaletica_orizzontale"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE segnalazioni DROP CONSTRAINT IF EXISTS segnalazioni_stato_check;"
    )
    op.execute(
        "ALTER TABLE segnalazioni "
        "ADD CONSTRAINT segnalazioni_stato_check "
        "CHECK (lower(stato) IN ('aperta','in lavorazione','chiusa'));"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE segnalazioni DROP CONSTRAINT IF EXISTS segnalazioni_stato_check;"
    )
