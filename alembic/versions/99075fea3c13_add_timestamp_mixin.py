"""add_timestamp_mixin

Revision ID: 99075fea3c13
Revises: c66d87245cfc
Create Date: 2026-03-07 22:38:50.351314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99075fea3c13'
down_revision: Union[str, Sequence[str], None] = 'c66d87245cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts(col: str, table: str) -> None:
    """Add a NOT NULL DateTime column with NOW() as default."""
    op.add_column(table, sa.Column(col, sa.DateTime(), nullable=False,
                                   server_default=sa.text("NOW()")))


def _bool_false(col: str, table: str) -> None:
    """Add a NOT NULL Boolean column defaulting to false."""
    op.add_column(table, sa.Column(col, sa.Boolean(), nullable=False,
                                   server_default=sa.text("false")))


def _soft_delete_cols(table: str) -> None:
    """Add SoftDeleteMixin columns: is_deleted, deleted_at, deleted_by."""
    _bool_false('is_deleted', table)
    op.add_column(table, sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column(table, sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, table, 'user', ['deleted_by'], ['id'])


def _audit_cols(table: str) -> None:
    """Add TimestampMixin audit columns: updated_at, created_by, updated_by."""
    _ts('updated_at', table)
    op.add_column(table, sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column(table, sa.Column('updated_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, table, 'user', ['created_by'], ['id'])
    op.create_foreign_key(None, table, 'user', ['updated_by'], ['id'])


def upgrade() -> None:
    """
    Add SoftDeleteMixin + TimestampMixin columns to all existing tables.

    What each table already has from previous migrations:
      - task:        id, title, description, completed, priority, due_date,
                     project_id, assigned_to, created_at, owner_id
      - project:     id, name, description, color, icon, owner_id, created_at
      - user:        id, email, google_id, hashed_password, name, created_at
      - label:       id, name, color, owner_id
      - reminder:    id, task_id, remind_at, sent
      - taskassignee: task_id, user_id
      - tasklabel:   task_id, label_id
      - team:        id, name, description, invite_code, color, icon, created_by, created_at
      - team_member: id, team_id, user_id, role, joined_at

    We do NOT drop owner_id — the API routers still reference it.
    """

    # ── label (no created_at yet) ──────────────────────────────────────
    _ts('created_at', 'label')
    _audit_cols('label')
    _soft_delete_cols('label')

    # ── project (already has created_at) ──────────────────────────────
    _audit_cols('project')
    _soft_delete_cols('project')

    # ── reminder (no created_at yet) ──────────────────────────────────
    _ts('created_at', 'reminder')
    _audit_cols('reminder')
    _soft_delete_cols('reminder')

    # ── task (already has created_at) ─────────────────────────────────
    _audit_cols('task')
    _soft_delete_cols('task')

    # ── taskassignee (no created_at yet) ──────────────────────────────
    _ts('created_at', 'taskassignee')
    _audit_cols('taskassignee')
    _soft_delete_cols('taskassignee')

    # ── tasklabel (no created_at yet) ─────────────────────────────────
    _ts('created_at', 'tasklabel')
    _audit_cols('tasklabel')
    _soft_delete_cols('tasklabel')

    # ── team (already has created_at + created_by) ────────────────────
    _ts('updated_at', 'team')
    op.add_column('team', sa.Column('updated_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'team', 'user', ['updated_by'], ['id'])
    # created_by was NOT NULL in the original team migration — make nullable
    op.alter_column('team', 'created_by', existing_type=sa.INTEGER(), nullable=True)
    _soft_delete_cols('team')

    # ── team_member (no created_at yet) ───────────────────────────────
    _ts('created_at', 'team_member')
    _audit_cols('team_member')
    _soft_delete_cols('team_member')

    # ── user (already has created_at) ─────────────────────────────────
    _audit_cols('user')
    _soft_delete_cols('user')


def downgrade() -> None:
    """Remove mixin columns. Note: owner_id was never touched so it stays."""

    # user
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'deleted_by')
    op.drop_column('user', 'deleted_at')
    op.drop_column('user', 'is_deleted')
    op.drop_column('user', 'updated_by')
    op.drop_column('user', 'created_by')
    op.drop_column('user', 'updated_at')

    # team_member
    op.drop_constraint(None, 'team_member', type_='foreignkey')
    op.drop_constraint(None, 'team_member', type_='foreignkey')
    op.drop_constraint(None, 'team_member', type_='foreignkey')
    op.drop_column('team_member', 'deleted_by')
    op.drop_column('team_member', 'deleted_at')
    op.drop_column('team_member', 'is_deleted')
    op.drop_column('team_member', 'updated_by')
    op.drop_column('team_member', 'created_by')
    op.drop_column('team_member', 'updated_at')
    op.drop_column('team_member', 'created_at')

    # team
    op.drop_constraint(None, 'team', type_='foreignkey')
    op.drop_constraint(None, 'team', type_='foreignkey')
    op.alter_column('team', 'created_by', existing_type=sa.INTEGER(), nullable=False)
    op.drop_column('team', 'deleted_by')
    op.drop_column('team', 'deleted_at')
    op.drop_column('team', 'is_deleted')
    op.drop_column('team', 'updated_by')
    op.drop_column('team', 'updated_at')

    # tasklabel
    op.drop_constraint(None, 'tasklabel', type_='foreignkey')
    op.drop_constraint(None, 'tasklabel', type_='foreignkey')
    op.drop_constraint(None, 'tasklabel', type_='foreignkey')
    op.drop_column('tasklabel', 'deleted_by')
    op.drop_column('tasklabel', 'deleted_at')
    op.drop_column('tasklabel', 'is_deleted')
    op.drop_column('tasklabel', 'updated_by')
    op.drop_column('tasklabel', 'created_by')
    op.drop_column('tasklabel', 'updated_at')
    op.drop_column('tasklabel', 'created_at')

    # taskassignee
    op.drop_constraint(None, 'taskassignee', type_='foreignkey')
    op.drop_constraint(None, 'taskassignee', type_='foreignkey')
    op.drop_constraint(None, 'taskassignee', type_='foreignkey')
    op.drop_column('taskassignee', 'deleted_by')
    op.drop_column('taskassignee', 'deleted_at')
    op.drop_column('taskassignee', 'is_deleted')
    op.drop_column('taskassignee', 'updated_by')
    op.drop_column('taskassignee', 'created_by')
    op.drop_column('taskassignee', 'updated_at')
    op.drop_column('taskassignee', 'created_at')

    # task
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'deleted_by')
    op.drop_column('task', 'deleted_at')
    op.drop_column('task', 'is_deleted')
    op.drop_column('task', 'updated_by')
    op.drop_column('task', 'created_by')
    op.drop_column('task', 'updated_at')

    # reminder
    op.drop_constraint(None, 'reminder', type_='foreignkey')
    op.drop_constraint(None, 'reminder', type_='foreignkey')
    op.drop_constraint(None, 'reminder', type_='foreignkey')
    op.drop_column('reminder', 'deleted_by')
    op.drop_column('reminder', 'deleted_at')
    op.drop_column('reminder', 'is_deleted')
    op.drop_column('reminder', 'updated_by')
    op.drop_column('reminder', 'created_by')
    op.drop_column('reminder', 'updated_at')
    op.drop_column('reminder', 'created_at')

    # project
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_column('project', 'deleted_by')
    op.drop_column('project', 'deleted_at')
    op.drop_column('project', 'is_deleted')
    op.drop_column('project', 'updated_by')
    op.drop_column('project', 'created_by')
    op.drop_column('project', 'updated_at')

    # label
    op.drop_constraint(None, 'label', type_='foreignkey')
    op.drop_constraint(None, 'label', type_='foreignkey')
    op.drop_constraint(None, 'label', type_='foreignkey')
    op.drop_column('label', 'deleted_by')
    op.drop_column('label', 'deleted_at')
    op.drop_column('label', 'is_deleted')
    op.drop_column('label', 'updated_by')
    op.drop_column('label', 'created_by')
    op.drop_column('label', 'updated_at')
    op.drop_column('label', 'created_at')
