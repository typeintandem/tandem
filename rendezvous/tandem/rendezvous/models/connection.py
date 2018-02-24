from tandem.shared.models.base import ModelBase


class Connection(ModelBase):
    def __init__(self, peer):
        self._peer = peer

    def __eq__(self, other):
        return self._peer == other._peer

    def get_id(self):
        return self._peer.get_id()

    def get_peer(self):
        return self._peer
