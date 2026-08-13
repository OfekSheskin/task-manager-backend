"""replace friendshipstatus enum values

Revision ID: 2d01b63b0cdb
Revises: 7e1c0ee3ac3b
Create Date: 2026-08-13 13:06:37.110571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d01b63b0cdb'
down_revision: Union[str, Sequence[str], None] = '7e1c0ee3ac3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_status = sa.Enum('PENDING', 'ACCEPTED', name='friendshipstatus')
new_status = sa.Enum('PENDING', 'APPROVED', 'DENIED', name='friendshipstatus')


def upgrade() -> None:
    """Upgrade schema."""
    # Postgres cannot remove a value from an existing enum type, so the type is
    # rebuilt: rename the old one aside, create the new one, convert the column,
    # then drop the leftover. ACCEPTED rows carry over as APPROVED.
    op.execute('ALTER TYPE friendshipstatus RENAME TO friendshipstatus_old')
    new_status.create(op.get_bind())
    op.execute(
        'ALTER TABLE friendships ALTER COLUMN status TYPE friendshipstatus '
        "USING (CASE WHEN status::text = 'ACCEPTED' THEN 'APPROVED' "
        'ELSE status::text END)::friendshipstatus'
    )
    op.execute('DROP TYPE friendshipstatus_old')


def downgrade() -> None:
    """Downgrade schema."""
    # DENIED has no equivalent in the old type, so those rows fall back to PENDING.
    op.execute('ALTER TYPE friendshipstatus RENAME TO friendshipstatus_new')
    old_status.create(op.get_bind())
    op.execute(
        'ALTER TABLE friendships ALTER COLUMN status TYPE friendshipstatus '
        "USING (CASE WHEN status::text = 'APPROVED' THEN 'ACCEPTED' "
        "WHEN status::text = 'DENIED' THEN 'PENDING' "
        'ELSE status::text END)::friendshipstatus'
    )
    op.execute('DROP TYPE friendshipstatus_new')
