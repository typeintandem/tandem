from sqlalchemy import orm, schema, types
from tandem.models.base import BaseModel


class Flow(BaseModel):
    __tablename__ = 'flows'
    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.String(255))
    url = schema.Column(types.String(255))
    frequency = schema.Column(types.Integer)
    viewport = schema.Column(types.ARRAY(types.Integer, dimensions=1))
    actions = orm.relationship('Action')
    runs = orm.relationship('Run')
