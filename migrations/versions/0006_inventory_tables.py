"""add inventory tables"""

from alembic import op
import sqlalchemy as sa

revision = "0006_inventory_tables"
down_revision = "0005_optional_times_for_day_off"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dispositivi",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("descrizione", sa.String(), nullable=True),
        sa.Column("anno", sa.Integer(), nullable=True),
    )
    op.create_index("ix_dispositivi_id", "dispositivi", ["id"])

    op.create_table(
        "segnaletica_temporanea",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("anno", sa.Integer(), nullable=True),
    )
    op.create_index("ix_segnaletica_temporanea_id", "segnaletica_temporanea", ["id"])

    op.create_table(
        "segnaletica_verticale",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("descrizione", sa.String(), nullable=False),
        sa.Column("anno", sa.Integer(), nullable=True),
    )
    op.create_index("ix_segnaletica_verticale_id", "segnaletica_verticale", ["id"])

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
    )
    op.create_index(
        "ix_segnaletica_orizzontale_items_id",
        "segnaletica_orizzontale_items",
        ["id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_segnaletica_orizzontale_items_id", table_name="segnaletica_orizzontale_items"
    )
    op.drop_table("segnaletica_orizzontale_items")

    op.drop_index(
        "ix_piani_segnaletica_orizzontale_id", table_name="piani_segnaletica_orizzontale"
    )
    op.drop_table("piani_segnaletica_orizzontale")

    op.drop_index("ix_segnaletica_verticale_id", table_name="segnaletica_verticale")
    op.drop_table("segnaletica_verticale")

    op.drop_index("ix_segnaletica_temporanea_id", table_name="segnaletica_temporanea")
    op.drop_table("segnaletica_temporanea")

    op.drop_index("ix_dispositivi_id", table_name="dispositivi")
    op.drop_table("dispositivi")

