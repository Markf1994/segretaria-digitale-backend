"""create initial tables"""

from alembic import op
import sqlalchemy as sa

revision = '0001_create_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('titolo', sa.String(), nullable=False),
        sa.Column('descrizione', sa.String(), nullable=True),
        sa.Column('data_ora', sa.DateTime(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
    )
    op.create_index('ix_events_id', 'events', ['id'])

    op.create_table(
        'pdf_files',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('filename'),
    )
    op.create_index('ix_pdf_files_id', 'pdf_files', ['id'])

    op.create_table(
        'determinazioni',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('capitolo', sa.String(), nullable=False),
        sa.Column('numero', sa.String(), nullable=False),
        sa.Column('descrizione', sa.String(), nullable=False),
        sa.Column('somma', sa.Float(), nullable=False),
        sa.Column('scadenza', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_determinazioni_id', 'determinazioni', ['id'])

    op.create_table(
        'todos',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('descrizione', sa.String(), nullable=False),
        sa.Column('scadenza', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
    )
    op.create_index('ix_todos_id', 'todos', ['id'])

def downgrade() -> None:
    op.drop_index('ix_todos_id', table_name='todos')
    op.drop_table('todos')
    op.drop_index('ix_determinazioni_id', table_name='determinazioni')
    op.drop_table('determinazioni')
    op.drop_index('ix_pdf_files_id', table_name='pdf_files')
    op.drop_table('pdf_files')
    op.drop_index('ix_events_id', table_name='events')
    op.drop_table('events')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
