"""add_kanban_columns

Revision ID: e10df047e825
Revises: 99075fea3c13
Create Date: 2026-03-09 21:48:58.742989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e10df047e825'
down_revision: Union[str, Sequence[str], None] = '99075fea3c13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Create kanban_column table (if not already auto-created by SQLModel) ──
    from sqlalchemy.engine import Inspector
    from alembic import op as _op
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    existing_tables = inspector.get_table_names()

    if 'kanban_column' not in existing_tables:
        op.create_table(
            'kanban_column',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('color', sa.String(), nullable=False, server_default='#6366F1'),
            sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('is_done_column', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            # TimestampMixin
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('updated_by', sa.Integer(), nullable=True),
            # SoftDeleteMixin
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('deleted_by', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['project.id']),
            sa.ForeignKeyConstraint(['created_by'], ['user.id']),
            sa.ForeignKeyConstraint(['updated_by'], ['user.id']),
            sa.ForeignKeyConstraint(['deleted_by'], ['user.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_kanban_column_project_id', 'kanban_column', ['project_id'])

    # ── Add column_id to task (if not already present) ─────────────────
    task_columns = [c['name'] for c in inspector.get_columns('task')]
    if 'column_id' not in task_columns:
        op.add_column('task', sa.Column('column_id', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'task', 'kanban_column', ['column_id'], ['id'])

    # ── Make owner_id nullable ──────────────────────────────────────────
    op.alter_column('label', 'owner_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('project', 'owner_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('task', 'owner_id', existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    op.alter_column('task', 'owner_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('project', 'owner_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('label', 'owner_id', existing_type=sa.INTEGER(), nullable=False)

    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'column_id')

    op.drop_index('ix_kanban_column_project_id', table_name='kanban_column')
    op.drop_table('kanban_column')
