from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState


class Peer(ModelBase):
    def __init__(self, address):
        self._address = address
        self._connection_state = ConnectionState.PING
        # If true, this agent initiated the connection to this peer
        self._initiated_connection = False

    def get_address(self):
        return self._address

    def get_connection_state(self):
        return self._connection_state
