"""Create orderstatus table and add initial statuses

Revision ID: 1205f13be0bf
Revises: None
Create Date: 2025-03-15 14:33:00
"""

from alembic import op
import sqlalchemy as sa

revision = '1205f13be0bf'
down_revision = '660eb0f181f3'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем начальные данные в существующую таблицу orderstatus
    op.bulk_insert(
        sa.table(
            'orderstatus',
            sa.column('id', sa.Integer),
            sa.column('status_text', sa.String)
        ),
        [
            {'id': 1, 'status_text': 'Создан'},
            {'id': 2, 'status_text': 'Подтверждён'},
            {'id': 3, 'status_text': 'Отменён'},
        ]
    )


def downgrade():
    # Удаляем добавленные данные при откате
    op.execute("DELETE FROM orderstatus WHERE id IN (1, 2, 3)")
