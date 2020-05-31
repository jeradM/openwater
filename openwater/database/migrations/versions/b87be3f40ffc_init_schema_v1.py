"""'init_schema_v1'

Revision ID: b87be3f40ffc
Revises:
Create Date: 2020-05-27 19:51:28.214632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b87be3f40ffc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plugin_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plugin_id", sa.String(length=50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plugin_config")),
    )
    op.create_table(
        "program",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(name="active_bool"), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=True),
        sa.Column("program_type", sa.String(length=20), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_program")),
    )
    op.create_table(
        "zone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(name="active_bool"), nullable=True),
        sa.Column("zone_type", sa.String(length=50), nullable=True),
        sa.Column("attrs", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_zone")),
    )
    op.create_table(
        "master_zones",
        sa.Column("zone_id", sa.Integer(), nullable=True),
        sa.Column("master_zone_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["master_zone_id"],
            ["zone.id"],
            name=op.f("fk_master_zones_master_zone_id_zone"),
        ),
        sa.ForeignKeyConstraint(
            ["zone_id"], ["zone.id"], name=op.f("fk_master_zones_zone_id_zone")
        ),
        sa.UniqueConstraint(
            "zone_id", "master_zone_id", name=op.f("uq_master_zones_zone_id")
        ),
    )


def downgrade():
    op.drop_table("master_zones")
    op.drop_table("zone")
    op.drop_table("program")
    op.drop_table("plugin_config")
