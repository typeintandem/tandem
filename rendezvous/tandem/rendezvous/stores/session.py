from tandem.shared.stores.base import StoreBase
from tandem.rendezvous.models.session import Session


class SessionStore(StoreBase):
    def __init__(self):
        self._sessions = {}

    def get_or_create_session(self, session_id):
        session = self._sessions.get(session_id, None)
        if session is None:
            session = Session(session_id)
            self._sessions[session_id] = session
        return session
