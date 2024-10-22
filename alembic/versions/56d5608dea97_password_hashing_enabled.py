"""password hashing enabled

Revision ID: 56d5608dea97
Revises: a052bdda46b1
Create Date: 2024-10-22 09:18:36.455043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56d5608dea97'
down_revision: Union[str, None] = 'a052bdda46b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
