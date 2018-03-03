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

    def get_session_from_address(self, address):
        for _, session in self._sessions.items():
            addresses = [
                connection.get_peer().get_private_address()
                for connection in session.get_connections()
            ]
            if address in addresses:
                return session
        return None
