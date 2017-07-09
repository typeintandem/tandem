from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from tandem import settings


class PostgreSQL():
    def __init__(self):
        self.DeclarativeBase = declarative_base()
        engine = create_engine(URL(**settings.POSTGRES_DATABASE))
        self.DeclarativeBase.metadata.create_all(engine)
