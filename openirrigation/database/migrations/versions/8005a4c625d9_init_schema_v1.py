"""'init_schema_v1'

Revision ID: 8005a4c625d9
Revises:
Create Date: 2020-05-21 06:35:33.630177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8005a4c625d9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'program',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('program_type', sa.String(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'zone',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('soil_type', sa.String(length=20), nullable=True),
        sa.Column('precip_rate', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'program_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.BigInteger(), nullable=True),
        sa.Column('zone_id', sa.Integer(), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['program.id'], ),
        sa.ForeignKeyConstraint(['zone_id'], ['zone.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('program_zones')
    op.drop_table('zone')
    op.drop_table('program')
