import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum, JSON

from tandem.database.instances import postgres


class ActionType(enum.Enum):
    http = 'HTTP'
    click = 'CLICK'
    key_press = 'KEY_PRESS'
    assert_url = 'ASSERT_URL'


class Action(postgres.DeclarativeBase):
    __tablename__ = 'actions'
    id = Column('id', Integer, primary_key=True)
    type = Column('type', Enum(ActionType))
    pre_delay = Column('pre_delay', Integer)
    post_delay = Column('post_delay', Integer)
    timestamp = Column('timestamp', Integer)
    attributes = Column('attributes', JSON)
    flow_id = Column(Integer, ForeignKey('flow.id'))
