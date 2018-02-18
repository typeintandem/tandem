from tandem.shared.models.base import ModelBase


class Peer(ModelBase):
    def __init__(self, id, address, connection_state):
        self._id = id
        self._address = address
        self._connection_state = connection_state

    def get_id(self):
        return self._id

    def get_address(self):
        return self._address

    def get_connection_state(self):
        return connection_state
