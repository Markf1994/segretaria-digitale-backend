"""create pdf_files table with uuid primary key"""

from alembic import op
import sqlalchemy as sa

revision = '0004_create_pdf_files_table'
down_revision = '0003_add_nome_to_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pdf_files',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False, unique=True),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_pdf_files_id', 'pdf_files', ['id'])


def downgrade() -> None:
    op.drop_index('ix_pdf_files_id', table_name='pdf_files')
    op.drop_table('pdf_files')
