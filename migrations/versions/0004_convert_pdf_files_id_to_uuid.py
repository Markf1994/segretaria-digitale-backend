"""convert pdf_files.id from integer to string UUID"""

from alembic import op
import sqlalchemy as sa
import uuid

revision = '0004_convert_pdf_files_id_to_uuid'
down_revision = '0003_add_nome_to_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pdf_files_new',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('filename'),
    )

    connection = op.get_bind()
    old = sa.table(
        'pdf_files',
        sa.column('title', sa.String()),
        sa.column('filename', sa.String()),
        sa.column('uploaded_at', sa.DateTime()),
    )
    new = sa.table(
        'pdf_files_new',
        sa.column('id', sa.String()),
        sa.column('title', sa.String()),
        sa.column('filename', sa.String()),
        sa.column('uploaded_at', sa.DateTime()),
    )
    rows = connection.execute(sa.select(old.c.title, old.c.filename, old.c.uploaded_at)).fetchall()
    for row in rows:
        connection.execute(
            new.insert().values(
                id=str(uuid.uuid4()),
                title=row.title,
                filename=row.filename,
                uploaded_at=row.uploaded_at,
            )
        )

    op.drop_index('ix_pdf_files_id', table_name='pdf_files')
    op.drop_table('pdf_files')
    op.rename_table('pdf_files_new', 'pdf_files')
    op.create_index('ix_pdf_files_id', 'pdf_files', ['id'])


def downgrade() -> None:
    op.create_table(
        'pdf_files_old',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('filename'),
    )

    connection = op.get_bind()
    new = sa.table(
        'pdf_files',
        sa.column('title', sa.String()),
        sa.column('filename', sa.String()),
        sa.column('uploaded_at', sa.DateTime()),
    )
    old = sa.table(
        'pdf_files_old',
        sa.column('id', sa.Integer()),
        sa.column('title', sa.String()),
        sa.column('filename', sa.String()),
        sa.column('uploaded_at', sa.DateTime()),
    )
    rows = connection.execute(sa.select(new.c.title, new.c.filename, new.c.uploaded_at)).fetchall()
    for row in rows:
        connection.execute(
            old.insert().values(
                title=row.title,
                filename=row.filename,
                uploaded_at=row.uploaded_at,
            )
        )

    op.drop_index('ix_pdf_files_id', table_name='pdf_files')
    op.drop_table('pdf_files')
    op.rename_table('pdf_files_old', 'pdf_files')
    op.create_index('ix_pdf_files_id', 'pdf_files', ['id'])
