"""post_cut_test_j

Revision ID: d5bd48ee2f6f
Revises: a5f818a67e30
Create Date: 2026-01-14 16:41:08.237423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5bd48ee2f6f'
down_revision: Union[str, Sequence[str], None] = 'a5f818a67e30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
