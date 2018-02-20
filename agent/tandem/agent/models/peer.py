from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState


class Peer(ModelBase):
    def __init__(self, address):
        self._address = address

    def get_id(self):
        return None

    def get_address(self):
        return self._address

    def get_connection_state(self):
        return ConnectionState.OPEN

    def set_connection_state(self, state):
        pass

    def append_handle(self, handle):
        pass

    def get_handles(self):
        return []

    def clear_handles(self):
        pass


class DirectPeer(Peer):
    def __init__(self, address):
        super(DirectPeer, self).__init__(address)


class HolePunchedPeer(Peer):
    def __init__(self, id, address, connection_state):
        super(HolePunchedPeer, self).__init__(address)
        self._id = id
        self._connection_state = connection_state
        self._handles = []

    def get_id(self):
        return self._id

    def get_connection_state(self):
        return self._connection_state

    def set_connection_state(self, state):
        self._connection_state = state

    def append_handle(self, handle):
        self._handles.append(handle)

    def get_handles(self):
        return self._handles

    def clear_handles(self):
        self._handles.clear()
