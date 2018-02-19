from tandem.shared.stores.base import StoreBase
from tandem.agent.models.connection_state import ConnectionState


class PeerStore(StoreBase):
    def __init__(self):
        self._peers = {}

    def get_peer(self, address):
        return self._peers.get(address, None)

    def get_peers(self, addresses=None):
        if addresses is None:
            return [peer for _, peer in self._peers.items()]

        return [self.get_peer(address) for address in addresses]

    def get_all_connected_peers(self):
        return [
            peer for _, peer in self._peers.items()
            if peer.get_connection_state() == ConnectionState.OPEN
        ]

    def get_peer_by_id(self, id):
        for _, peer in self._peers.items():
            if peer.get_id() == id:
                return peer
        return None

    def add_peer(self, peer):
        self._peers[peer.get_address()] = peer

    def remove_peer(self, peer):
        del self._peers[peer.get_address()]
