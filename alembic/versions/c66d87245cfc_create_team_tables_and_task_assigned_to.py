"""create_team_tables_and_task_assigned_to

Revision ID: c66d87245cfc
Revises: 95a3613ad517
Create Date: 2026-03-01 22:46:03.714113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c66d87245cfc'
down_revision: Union[str, Sequence[str], None] = '95a3613ad517'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ── Create team table ──────────────────────────────────────────
    op.create_table('team',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('invite_code', sa.String(), nullable=False),
        sa.Column('color', sa.String(), nullable=False, server_default='#6366F1'),
        sa.Column('icon', sa.String(), nullable=False, server_default='group'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_team_invite_code', 'team', ['invite_code'], unique=True)

    # ── Create project_team join table ─────────────────────────────
    op.create_table('project_team',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id']),
        sa.ForeignKeyConstraint(['team_id'], ['team.id']),
        sa.PrimaryKeyConstraint('project_id', 'team_id'),
    )

    # ── Create team_member table ───────────────────────────────────
    op.create_table('team_member',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['team.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_team_member_team_id', 'team_member', ['team_id'], unique=False)
    op.create_index('ix_team_member_user_id', 'team_member', ['user_id'], unique=False)

    # ── Add assigned_to to task ────────────────────────────────────
    op.add_column('task', sa.Column('assigned_to', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_assigned_to_user', 'task', 'user', ['assigned_to'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_task_assigned_to_user', 'task', type_='foreignkey')
    op.drop_column('task', 'assigned_to')
    op.drop_index('ix_team_member_user_id', table_name='team_member')
    op.drop_index('ix_team_member_team_id', table_name='team_member')
    op.drop_table('team_member')
    op.drop_table('project_team')
    op.drop_index('ix_team_invite_code', table_name='team')
    op.drop_table('team')
