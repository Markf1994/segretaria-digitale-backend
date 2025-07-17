"""convert segnalazioni tipo and stato to enum"""

from alembic import op
import sqlalchemy as sa
from app.schemas.segnalazione import TipoSegnalazione, StatoSegnalazione

revision = "0009_convert_tipo_stato_to_enum"
down_revision = "0008_create_segnalazioni_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tipo_enum = sa.Enum(TipoSegnalazione, name="tipo_segnalazione")
    stato_enum = sa.Enum(StatoSegnalazione, name="stato_segnalazione")

    bind = op.get_bind()
    tipo_enum.create(bind, checkfirst=True)
    stato_enum.create(bind, checkfirst=True)

    op.alter_column(
        "segnalazioni",
        "tipo",
        existing_type=sa.String(),
        type_=tipo_enum,
        postgresql_using="tipo::tipo_segnalazione",
    )
    op.alter_column(
        "segnalazioni",
        "stato",
        existing_type=sa.String(),
        type_=stato_enum,
        postgresql_using="stato::stato_segnalazione",
    )


def downgrade() -> None:
    tipo_enum = sa.Enum(TipoSegnalazione, name="tipo_segnalazione")
    stato_enum = sa.Enum(StatoSegnalazione, name="stato_segnalazione")

    op.alter_column(
        "segnalazioni",
        "tipo",
        existing_type=tipo_enum,
        type_=sa.String(),
        postgresql_using="tipo::text",
    )
    op.alter_column(
        "segnalazioni",
        "stato",
        existing_type=stato_enum,
        type_=sa.String(),
        postgresql_using="stato::text",
    )

    bind = op.get_bind()
    tipo_enum.drop(bind, checkfirst=True)
    stato_enum.drop(bind, checkfirst=True)
