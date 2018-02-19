from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState
from tandem.agent.models.peer import HolePunchedPeer


class PingingPeer(ModelBase):
    PROMOTE_AFTER = 3

    def __init__(self, id, addresses, initiated_connection=False):
        self._id = id
        # If true, this agent initiated the connection to this peer
        self._initiated_connection = initiated_connection
        self._addresses = addresses
        self._address_ping_counts = {address: 0 for address in addresses}

    def get_id(self):
        return self._id

    def get_addresses(self):
        return self._addresses

    def initiated_connection(self):
        return self._initiated_connection

    def bump_ping_count(self, address):
        if address in self._address_ping_counts:
            self._address_ping_counts[address] += 1

    def maybe_promote_to_peer(self):
        active_address = self._get_active_address()
        if active_address is None:
            return None
        peer_connection_state = (
            ConnectionState.SEND_SYN if self._initiated_connection
            else ConnectionState.WAIT_FOR_SYN
        )
        return HolePunchedPeer(self._id, active_address, peer_connection_state)

    def _get_active_address(self):
        for address, replies_received in self._address_ping_counts.items():
            if replies_received >= PingingPeer.PROMOTE_AFTER:
                return address
        return None
