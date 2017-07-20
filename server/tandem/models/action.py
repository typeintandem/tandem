import enum
from sqlalchemy import schema, types
from tandem.models.base import BaseModel
from tandem.models.flow import Flow


class ActionType(enum.Enum):
    http = 'HTTP'
    click = 'CLICK'
    key_press = 'KEY_PRESS'
    assert_url = 'ASSERT_URL'

    def __str__(self):
        return str(self.value)


class Action(BaseModel):
    __tablename__ = 'actions'
    id = schema.Column('id', types.Integer, primary_key=True)
    type = schema.Column('type', types.Enum(ActionType))
    pre_delay = schema.Column('pre_delay', types.Integer)
    post_delay = schema.Column('post_delay', types.Integer)
    timestamp = schema.Column('timestamp', types.Integer)
    attributes = schema.Column('attributes', types.JSON)
    step = schema.Column('step', types.Integer)
    flow_id = schema.Column(types.Integer, schema.ForeignKey(Flow.__table__.c.id))
