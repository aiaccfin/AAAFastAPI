"""post_cut_test

Revision ID: f4ca3a6fcb1f
Revises: 3dfe2e78d835
Create Date: 2026-01-14 15:13:51.098276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4ca3a6fcb1f'
down_revision: Union[str, Sequence[str], None] = '3dfe2e78d835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
