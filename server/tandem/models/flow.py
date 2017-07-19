from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from tandem.database.instances import postgres


class Flow(postgres.DeclarativeBase):
    __tablename__ = 'flows'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(255))
    frequency = Column('frequency', Integer)
    viewport = Column('viewport', postgresql.ARRAY(Integer, dimensions=1))
    actions = relationship("Action")

    def __init__(self, name, frequency, viewport):
        self.name = name
        self.frequency = frequency
        self.viewport = viewport

    def add_action(self, action):
        pass

    def get_by_id(flow_id):
        pass

    def get_by_ids(flow_ids):
        return [instance for instance in postgres.new_session().
                query(Flow).filter(Flow.id.in_(flow_ids))]
