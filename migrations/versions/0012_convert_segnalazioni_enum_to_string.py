"""convert segnalazioni columns tipo and stato to string"""

from alembic import op
import sqlalchemy as sa
from app.schemas.segnalazione import TipoSegnalazione, StatoSegnalazione

revision = "0012_convert_segnalazioni_enum_to_string"
down_revision = "0011_update_segnalazioni_stato_check"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tipo_enum = sa.Enum(TipoSegnalazione, name="tiposegnalazione")
    stato_enum = sa.Enum(StatoSegnalazione, name="statosegnalazione")

    op.alter_column(
        "segnalazioni",
        "tipo",
        existing_type=tipo_enum,
        type_=sa.String(length=30),
        postgresql_using="tipo::text",
    )
    op.alter_column(
        "segnalazioni",
        "stato",
        existing_type=stato_enum,
        type_=sa.String(length=30),
        postgresql_using="stato::text",
    )

    bind = op.get_bind()
    tipo_enum.drop(bind, checkfirst=True)
    stato_enum.drop(bind, checkfirst=True)

    op.execute(
        "ALTER TABLE segnalazioni DROP CONSTRAINT IF EXISTS segnalazioni_stato_check;"
    )
    op.execute(
        "ALTER TABLE segnalazioni ADD CONSTRAINT segnalazioni_stato_check CHECK (lower(stato) IN ('aperta','in lavorazione','chiusa'));"
    )


def downgrade() -> None:
    tipo_enum = sa.Enum(TipoSegnalazione, name="tiposegnalazione")
    stato_enum = sa.Enum(StatoSegnalazione, name="statosegnalazione")

    tipo_enum.create(op.get_bind(), checkfirst=True)
    stato_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "segnalazioni",
        "tipo",
        existing_type=sa.String(length=30),
        type_=tipo_enum,
        postgresql_using="tipo::tiposegnalazione",
    )
    op.alter_column(
        "segnalazioni",
        "stato",
        existing_type=sa.String(length=30),
        type_=stato_enum,
        postgresql_using="stato::statosegnalazione",
    )

    op.execute(
        "ALTER TABLE segnalazioni DROP CONSTRAINT IF EXISTS segnalazioni_stato_check;"
    )
    op.execute(
        "ALTER TABLE segnalazioni ADD CONSTRAINT segnalazioni_stato_check CHECK (lower(stato) IN ('aperta','in lavorazione','chiusa'));"
    )
