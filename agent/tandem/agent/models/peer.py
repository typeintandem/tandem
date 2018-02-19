from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState


class Peer(ModelBase):
    def __init__(self, address):
        self._address = address

    def get_address(self):
        return self._address

    def get_connection_state(self):
        return ConnectionState.OPEN


class DirectPeer(Peer):
    def __init__(self, address):
        super(DirectPeer, self).__init__(address)


class HolePunchedPeer(Peer):
    def __init__(self, id, address, connection_state):
        super(HolePunchedPeer, self).__init__(address)
        self._id = id
        self._connection_state = connection_state

    def get_id(self):
        return self._id

    def get_connection_state(self):
        return self._connection_state
