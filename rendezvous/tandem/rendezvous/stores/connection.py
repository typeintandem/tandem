from tandem.shared.stores.base import StoreBase


class ConnectionStore(StoreBase):
    def __init__(self):
        self._connections = {}

    def get_connection(self, address):
        return self._connections.get(address, None)

    def get_connections(self, addresses):
        return [self.get_connection(address) for address in addresses]

    def register_connection(self, connection):
        self._connections[connection.get_address()] = connection
