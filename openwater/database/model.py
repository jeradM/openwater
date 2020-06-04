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
    Time,
    Date,
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
    Column("zone_type", String(50), nullable=False),
    Column("is_master", Boolean(name="is_master_bool"), default=False),
    Column("attrs", JSON),
)

zone_run = Table(
    "zone_run",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("zone_id", Integer, ForeignKey("zone.id"), nullable=False),
    Column("start", DateTime),
    Column("duration", Integer),
)

master_zone_join = Table(
    "master_zones",
    metadata,
    Column("zone_id", Integer, ForeignKey("zone.id")),
    Column("master_zone_id", Integer, ForeignKey("zone.id")),
    UniqueConstraint("zone_id", "master_zone_id"),
)

program = Table(
    "program",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("program_type", String(20), nullable=False),
    Column("attrs", JSON, nullable=False),
)

program_run = Table(
    "program_run",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("program_id", Integer, ForeignKey("program.id"), nullable=False),
    Column("schedule_id", Integer, ForeignKey("schedule.id"), nullable=False),
    Column("start", DateTime),
    Column("end", DateTime),
)

program_step = Table(
    "program_step",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("program_id", Integer, ForeignKey("program.id"), nullable=False),
    Column("order", Integer, nullable=False),
)

program_action = Table(
    "program_action",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("step_id", Integer, ForeignKey("program_step.id"), nullable=False),
    Column("action_type", String(10), nullable=False),
    Column("duration", Integer, nullable=False),
)

program_action_zones = Table(
    "program_action_zones",
    metadata,
    Column("action_id", Integer, ForeignKey("program_action.id"), nullable=False),
    Column("zone_id", Integer, ForeignKey("zone.id"), nullable=False),
    UniqueConstraint("action_id", "zone_id"),
)

plugin_config = Table(
    "plugin_config",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("plugin_id", String(50)),
    Column("version", Integer),
    Column("config", JSON),
)

schedule = Table(
    "schedule",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("program_id", Integer, ForeignKey("program.id"), nullable=False),
    Column("enabled", Boolean(name="enabled_bool"), nullable=False, default=False),
    Column("at", Integer, nullable=False),
    Column("day_interval", Integer),
    Column("days_restriction", String(1)),
    Column("dow_mask", Integer),
    Column("minute_interval", Integer),
    Column("on_day", Date),
    Column("start_day", Date),
)
