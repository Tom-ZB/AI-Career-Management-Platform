"""add deadline column to job_opportunities

Revision ID: 001
Revises:
Create Date: 2026-08-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None  # First migration, no previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add deadline column to job_opportunities table."""
    # Check if deadline column exists first
    with op.batch_alter_table('job_opportunities') as batch_op:
        try:
            batch_op.add_column(sa.Column('deadline', sa.Date(), nullable=True, comment='Application deadline date'))
        except Exception:
            # Column might already exist, ignore error
            pass


def downgrade():
    """Remove deadline column from job_opportunities table."""
    with op.batch_alter_table('job_opportunities') as batch_op:
        batch_op.drop_column('deadline')
