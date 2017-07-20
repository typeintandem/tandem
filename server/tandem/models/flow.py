from sqlalchemy import orm, schema, types
from tandem.models.base import BaseModel


class Flow(BaseModel):
    __tablename__ = 'flows'
    id = schema.Column('id', types.Integer, primary_key=True)
    name = schema.Column('name', types.String(255))
    frequency = schema.Column('frequency', types.Integer)
    viewport = schema.Column('viewport', types.ARRAY(types.Integer, dimensions=1))
    actions = orm.relationship("Action")
