from tandem.database import postgresql
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    def as_dict(self):
        res = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key in res.keys():
            if isinstance(res[key], object) and getattr(res[key], 'as_dict', False):
                res[key] = res[key].to_json()
            else:
                res[key] = str(res[key])
        return res


BaseModel = declarative_base(cls=Base)
BaseModel.query = postgresql.session.query_property()
