from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState
from tandem.agent.models.peer import HolePunchedPeer


class PingingPeer(ModelBase):
    PROMOTE_AFTER = 3

    def __init__(
        self,
        id,
        public_address,
        private_address,
        initiated_connection=False,
    ):
        self._id = id
        # If true, this agent initiated the connection to this peer
        self._initiated_connection = initiated_connection
        self._public_address = public_address
        self._private_address = private_address
        self._address_ping_counts = {
            self._public_address: 0,
            self._private_address: 0,
        }
        self._ping_interval_handle = None

    def get_id(self):
        return self._id

    def get_addresses(self):
        return [self._public_address, self._private_address]

    def set_ping_interval_handle(self, ping_interval_handle):
        self._ping_interval_handle = ping_interval_handle

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
        if self._ping_interval_handle is not None:
            self._ping_interval_handle.cancel()
        return HolePunchedPeer(self._id, active_address, peer_connection_state)

    def _get_active_address(self):
        private_address_count = \
            self._address_ping_counts[self._private_address]
        public_address_count = self._address_ping_counts[self._public_address]

        # Prefer private address
        if private_address_count > 0:
            return (
                self._private_address
                if private_address_count >= PingingPeer.PROMOTE_AFTER
                else None
            )
        else:
            return (
                self._public_address
                if public_address_count >= PingingPeer.PROMOTE_AFTER
                else None
            )
