from tandem.models.base import BaseModel
from tandem.database import postgresql

BaseModel.metadata.create_all(postgresql.engine)
