"""post_cut_test_j

Revision ID: a5f818a67e30
Revises: f4ca3a6fcb1f
Create Date: 2026-01-14 15:16:37.743948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5f818a67e30'
down_revision: Union[str, Sequence[str], None] = 'f4ca3a6fcb1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
