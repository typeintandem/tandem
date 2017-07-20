from tandem.database import postgresql
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


BaseModel = declarative_base(cls=Base)
BaseModel.query = postgresql.session.query_property()
