from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tandem import settings

DeclarativeBase = declarative_base()


class PostgreSQL():
    def __init__(self):
        self._engine = create_engine(URL(**settings.POSTGRES_DATABASE))
        self._Session = sessionmaker(bind=self._engine)
        DeclarativeBase.metadata.create_all(self._engine)

    def new_session(self):
        return self._Session()
