from tandem.shared.stores.base import StoreBase


class PeerStore(StoreBase):
    def __init__(self):
        self._peers = {}

    def get_peer(self, address):
        return self._peers.get(address, None)

    def get_peers(self, addresses=None):
        if addresses is None:
            addresses = [address for address in self._peers]

        return [self.get_peer(address) for address in addresses]

    def add_peer(self, peer):
        self._peers[peer.get_address()] = peer

    def remove_peer(self, peer):
        del self._peers[peer.get_address()]
