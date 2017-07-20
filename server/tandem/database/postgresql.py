from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker
from tandem import settings


class PostgreSQL():
    def __init__(self):
        self.engine = create_engine(URL(**settings.POSTGRES_DATABASE))
        self.session = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        ))
