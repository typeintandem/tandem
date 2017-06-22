import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum, JSON

from tandem.database.postgresql import DeclarativeBase


class ActionType(enum.Enum):
    http = 1
    click = 2
    key_press = 3
    assert_url = 4


class Action(DeclarativeBase):
    __tablename__ = 'actions'
    id = Column("id", Integer, primary_key=True)
    type = Column("type", Enum(ActionType))
    pre_delay = Column("pre_delay", Integer)
    post_delay = Column("post_delay", Integer)
    timestamp = Column("timestamp", Integer)
    attributes = Column("attributes", JSON)
    flow_id = Column(Integer, ForeignKey('flow.id'))
