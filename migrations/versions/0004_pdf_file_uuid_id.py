"""convert pdf file id to uuid string"""

from alembic import op
import sqlalchemy as sa
import uuid

revision = '0004_pdf_file_uuid_id'
down_revision = '0003_add_nome_to_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # add temporary uuid column
    with op.batch_alter_table('pdf_files') as batch_op:
        batch_op.add_column(sa.Column('id_new', sa.String(), nullable=True))

    # populate with new uuids
    results = conn.execute(sa.text('SELECT id FROM pdf_files')).fetchall()
    for row in results:
        conn.execute(
            sa.text('UPDATE pdf_files SET id_new = :uuid WHERE id = :old_id'),
            {'uuid': str(uuid.uuid4()), 'old_id': row[0]},
        )

    # drop old id and rename new column
    with op.batch_alter_table('pdf_files') as batch_op:
        batch_op.drop_index('ix_pdf_files_id')
        batch_op.drop_column('id')
        batch_op.alter_column('id_new', new_column_name='id', nullable=False)
        batch_op.create_index('ix_pdf_files_id', ['id'])


def downgrade() -> None:
    conn = op.get_bind()
    with op.batch_alter_table('pdf_files') as batch_op:
        batch_op.drop_index('ix_pdf_files_id')
        batch_op.add_column(sa.Column('id_old', sa.Integer(), autoincrement=True, nullable=True))

    results = conn.execute(sa.text('SELECT id FROM pdf_files')).fetchall()
    counter = 1
    for row in results:
        conn.execute(
            sa.text('UPDATE pdf_files SET id_old = :new_id WHERE id = :uuid'),
            {'new_id': counter, 'uuid': row[0]},
        )
        counter += 1

    with op.batch_alter_table('pdf_files') as batch_op:
        batch_op.drop_column('id')
        batch_op.alter_column('id_old', new_column_name='id', nullable=False)
        batch_op.create_index('ix_pdf_files_id', ['id'])
