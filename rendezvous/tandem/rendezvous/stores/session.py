from uuid import uuid4
from tandem.shared.stores.base import StoreBase
from tandem.rendezvous.models.session import Session


class SessionStore(StoreBase):
    def __init__(self):
        self._sessions = {}

    def get_session(self, session_id):
        return self._sessions.get(session_id, None)

    def new_session(self):
        session_id = uuid4()
        self._sessions[session_id] = Session(session_id)
        return (session_id, self._sessions[session_id])
