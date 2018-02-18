from tandem.shared.stores.base import StoreBase


class PingingPeerStore(StoreBase):
    """
    Stores peers currently being pinged to determine an active address.
    """
    def __init__(self):
        self._peers = {}

    def add_peer(self, peer):
        self._peers[peer.get_id()] = peer

    def remove_peer(self, peer):
        del self._peers[peer.get_id()]

    def get_peer(self, id):
        return self._peers.get(id, None)
