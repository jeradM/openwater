from sqlalchemy import Column, Integer, String, Boolean, Numeric, BigInteger, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

SCHEMA_VERSION = 1

Base = declarative_base()


class MZone(Base):
    __tablename__ = 'zone'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    active = Column(Boolean)
    soil_type = Column(String(20))
    precip_rate = Column(Numeric(6, 3))


class MProgram(Base):
    __tablename__ = 'program'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean)
    start_at = Column(DateTime)
    program_type = Column(String)
    priority = Column(Integer)
    zones = relationship('MProgramZone', back_populates='program')


class MProgramZone(Base):
    __tablename__ = 'program_zones'

    id = Column(Integer, primary_key=True)
    duration = Column(BigInteger)
    zone_id = Column(Integer, ForeignKey('zone.id'))
    program_id = Column(Integer, ForeignKey('program.id'))
    order = Column(Integer)

    zone = relationship('MZone', uselist=False)
    program = relationship('MProgram', uselist=False, back_populates='zones')
