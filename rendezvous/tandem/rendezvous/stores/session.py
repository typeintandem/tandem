from tandem.shared.stores.base import StoreBase
from tandem.rendezvous.models.session import Session


class SessionStore(StoreBase):
    def __init__(self):
        self._sessions = {}

    def get_session_with_uuid(self, uuid):
        session = self._sessions.get(uuid, None)
        if not session:
            session = Session(uuid)
            self._sessions[uuid] = session
        return session
