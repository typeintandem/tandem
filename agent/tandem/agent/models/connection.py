from tandem.shared.models.base import ModelBase
from tandem.agent.models.connection_state import ConnectionState
import logging


class Connection(ModelBase):
    def __init__(self, peer):
        self._peer = peer

    def get_id(self):
        return self._peer.get_id()

    def get_active_address(self):
        raise NotImplementedError

    def get_connection_state(self):
        raise NotImplementedError

    def set_connection_state(self, state):
        raise NotImplementedError

    def is_relayed(self):
        return self.get_connection_state() == ConnectionState.RELAY

    def get_peer(self):
        return self._peer


class DirectConnection(Connection):
    """
    A connection to a peer established without using hole punching.
    """
    def __init__(self, peer):
        super(DirectConnection, self).__init__(peer)

    def get_active_address(self):
        return self.get_peer().get_public_address()

    def get_connection_state(self):
        return ConnectionState.OPEN

    def set_connection_state(self, state):
        pass


class HolePunchedConnection(Connection):
    """
    A connection to a peer that was established with hole punching.
    """
    PROMOTE_AFTER = 3

    def __init__(self, peer, initiated_connection):
        super(HolePunchedConnection, self).__init__(peer)
        self._active_address = None
        self._interval_handle = None
        self._connection_state = ConnectionState.PING
        # If true, this agent initiated the connection to this peer
        self._initiated_connection = initiated_connection

        self._address_ping_counts = {}
        self._address_ping_counts[peer.get_public_address()] = 0
        if peer.get_private_address() is not None:
            self._address_ping_counts[peer.get_private_address()] = 0

    def get_active_address(self):
        if self._active_address is None:
            self._active_address = self._compute_active_address()
        return self._active_address

    def get_connection_state(self):
        return self._connection_state

    def set_connection_state(self, state):
        if self._connection_state == state:
            return
        self._connection_state = state
        if self._interval_handle is not None:
            self._interval_handle.cancel()
            self._interval_handle = None

    def set_interval_handle(self, interval_handle):
        self._interval_handle = interval_handle

    def bump_ping_count(self, address):
        if address in self._address_ping_counts:
            self._address_ping_counts[address] += 1

    def initiated_connection(self):
        return self._initiated_connection

    def _compute_active_address(self):
        if self.is_relayed():
            return self.get_peer().get_public_address()

        private_address = self.get_peer().get_private_address()
        private_address_count = (
            self._address_ping_counts[private_address]
            if private_address is not None else 0
        )

        # If the private address is routable, always choose it
        if private_address_count > 0:
            return (
                private_address
                if private_address_count >= HolePunchedConnection.PROMOTE_AFTER
                else None
            )

        public_address = self.get_peer().get_public_address()
        public_address_count = self._address_ping_counts[public_address]
        return (
            public_address
            if public_address_count >= HolePunchedConnection.PROMOTE_AFTER
            else None
        )
