from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    Table,
    JSON,
    MetaData,
    UniqueConstraint,
)

SCHEMA_VERSION = 1

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

zone = Table(
    "zone",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("active", Boolean(name="active_bool"), default=True),
    Column("zone_type", String(50)),
    Column("attrs", JSON),
)

program = Table(
    "program",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("active", Boolean(name="active_bool")),
    Column("start_at", DateTime),
    Column("program_type", String(20)),
    Column("priority", Integer()),
)

plugin_config = Table(
    "plugin_config",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("plugin_id", String(50)),
    Column("version", Integer),
    Column("config", JSON),
)

master_zone_join = Table(
    "master_zones",
    metadata,
    Column("zone_id", Integer, ForeignKey("zone.id")),
    Column("master_zone_id", Integer, ForeignKey("zone.id")),
    UniqueConstraint("zone_id", "master_zone_id"),
)
