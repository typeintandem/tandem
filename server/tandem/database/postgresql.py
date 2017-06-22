from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from tandem import settings

DeclarativeBase = declarative_base()


def initialize():
    engine = create_engine(URL(**settings.POSTGRES_DATABASE))
    DeclarativeBase.metadata.create_all(engine)
