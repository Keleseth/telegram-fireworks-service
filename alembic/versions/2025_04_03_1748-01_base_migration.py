"""base_migration

Revision ID: 01
Revises:
Create Date: 2025-04-03 17:48:10.483453

"""
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('id')
    )
    op.create_table('botinfo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('bot_info', sa.Text(), nullable=False),
    sa.Column('about_company', sa.Text(), nullable=False),
    sa.Column('contacts', sa.Text(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('parent_category_id', sa.Integer(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['parent_category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('discount',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('value', sa.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('media',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('media_url', sa.String(), nullable=False),
    sa.Column('media_type', sa.String(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('media_url')
    )
    op.create_table('newsletter',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('number_of_orders', sa.Integer(), nullable=False),
    sa.Column('age_verified', sa.Boolean(), nullable=False),
    sa.Column('datetime_send', sa.DateTime(), nullable=False),
    sa.Column('switch_send', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('account_age', sa.Enum('LESS_3_MONTHS', 'FROM_3_TO_12_MONTHS', 'FROM_1_TO_3_YEARS', 'MORE_THAN_3_YEARS', name='account_age_enum'), nullable=True),
    sa.Column('users_related_to_tag', sa.Boolean(), nullable=True),
    sa.Column('canceled', sa.Boolean(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('newslettermedia',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('media_url', sa.String(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orderstatus',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status_text', sa.String(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('property_field',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('field_name', sa.String(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('field_name'),
    sa.UniqueConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('nickname', sa.String(), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('age_verified', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('nickname'),
    sa.UniqueConstraint('phone_number'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('firework',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('measurement_unit', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('charges_count', sa.Integer(), nullable=True),
    sa.Column('effects_count', sa.Integer(), nullable=True),
    sa.Column('product_size', sa.String(), nullable=False),
    sa.Column('packing_material', sa.String(), nullable=True),
    sa.Column('article', sa.String(), nullable=False),
    sa.Column('caliber', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('formattedmedia',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file', sa.LargeBinary(), nullable=False),
    sa.Column('media_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['media_id'], ['media.id'], ),
    sa.PrimaryKeyConstraint('id', 'media_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('newslettermedialink',
    sa.Column('newsletter_id', sa.Integer(), nullable=False),
    sa.Column('media_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['media_id'], ['newslettermedia.id'], ),
    sa.ForeignKeyConstraint(['newsletter_id'], ['newsletter.id'], ),
    sa.PrimaryKeyConstraint('newsletter_id', 'media_id')
    )
    op.create_table('newslettertag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('newsletter_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['newsletter_id'], ['newsletter.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'newsletter_id')
    )
    op.create_table('useraddress',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['address_id'], ['address.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id', 'address_id', name='unique_user_address')
    )
    op.create_table('cart',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('price_per_unit', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('amount >= 1', name='min_cart_amount'),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id', 'firework_id', name='unique_cart_item')
    )
    op.create_table('favoritefirework',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id', 'firework_id', name='unique_favorite')
    )
    op.create_table('firework_media',
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ),
    sa.ForeignKeyConstraint(['image_id'], ['media.id'], ),
    sa.PrimaryKeyConstraint('firework_id', 'image_id')
    )
    op.create_table('firework_property',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('field_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['field_id'], ['property_field.id'], ),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('firework_tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'firework_id')
    )
    op.create_table('fireworkdiscount',
    sa.Column('firework_id', sa.Integer(), nullable=False),
    sa.Column('discount_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['discount_id'], ['discount.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('firework_id', 'discount_id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('user_address_id', sa.Integer(), nullable=True),
    sa.Column('fio', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('operator_call', sa.Boolean(), nullable=False),
    sa.Column('total', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['status_id'], ['orderstatus.id'], ),
    sa.ForeignKeyConstraint(['user_address_id'], ['useraddress.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('orderfirework',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('firework_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('price_per_unit', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['firework_id'], ['firework.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###

# Создание функции для обновления total
    op.execute("""
        CREATE OR REPLACE FUNCTION update_order_total()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE "order"
            SET total = (
                SELECT COALESCE(SUM(ofw.amount * ofw.price_per_unit), 0)
                FROM orderfirework ofw
                WHERE ofw.order_id = NEW.order_id
            )
            WHERE id = NEW.order_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Создание триггера
    op.execute("""
        CREATE TRIGGER trigger_update_order_total
        AFTER INSERT OR UPDATE OR DELETE ON orderfirework
        FOR EACH ROW EXECUTE FUNCTION update_order_total();
    """)


def downgrade() -> None:
    # Удаление триггера и функции
    op.execute('DROP TRIGGER IF EXISTS trigger_update_order_total ON orderfirework;')
    op.execute('DROP FUNCTION IF EXISTS update_order_total;')
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orderfirework')
    op.drop_table('order')
    op.drop_table('fireworkdiscount')
    op.drop_table('firework_tag')
    op.drop_table('firework_property')
    op.drop_table('firework_media')
    op.drop_table('favoritefirework')
    op.drop_table('cart')
    op.drop_table('useraddress')
    op.drop_table('newslettertag')
    op.drop_table('newslettermedialink')
    op.drop_table('formattedmedia')
    op.drop_table('firework')
    op.drop_table('user')
    op.drop_table('tag')
    op.drop_table('property_field')
    op.drop_table('orderstatus')
    op.drop_table('newslettermedia')
    op.drop_table('newsletter')
    op.drop_table('media')
    op.drop_table('discount')
    op.drop_table('category')
    op.drop_table('botinfo')
    op.drop_table('address')
    # ### end Alembic commands ###
