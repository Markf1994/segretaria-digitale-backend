"""remove piani_segnaletica_orizzontale and segnaletica_orizzontale_items tables"""

from alembic import op
import sqlalchemy as sa

revision = "0013_remove_horizontal_tables"
down_revision = "0012_convert_segnalazioni_enum_to_string"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "ix_segnaletica_orizzontale_items_id",
        table_name="segnaletica_orizzontale_items",
    )
    op.drop_table("segnaletica_orizzontale_items")

    op.drop_index(
        "ix_piani_segnaletica_orizzontale_id",
        table_name="piani_segnaletica_orizzontale",
    )
    op.drop_table("piani_segnaletica_orizzontale")


def downgrade() -> None:
    op.create_table(
        "piani_segnaletica_orizzontale",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("anno", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_piani_segnaletica_orizzontale_id",
        "piani_segnaletica_orizzontale",
        ["id"],
    )

    op.create_table(
        "segnaletica_orizzontale_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "piano_id",
            sa.String(),
            sa.ForeignKey("piani_segnaletica_orizzontale.id"),
            nullable=False,
        ),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("quantita", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("luogo", sa.String(), nullable=True),
        sa.Column("data", sa.Date(), nullable=True),
    )
    op.create_index(
        "ix_segnaletica_orizzontale_items_id",
        "segnaletica_orizzontale_items",
        ["id"],
    )
