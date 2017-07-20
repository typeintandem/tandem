from sqlalchemy import schema, types
from tandem.models.base import BaseModel
from tandem.models.flow import Flow


class Run(BaseModel):
    __tablename__ = 'run'
    id = schema.Column(types.Integer, primary_key=True)
    flow_id = schema.Column(types.Integer, schema.ForeignKey(Flow.__table__.c.id))
    result = schema.Column(types.String(255))
    submit_time = schema.Column(types.Integer)
    start_time = schema.Column(types.Integer)
    complete_time = schema.Column(types.Integer)
