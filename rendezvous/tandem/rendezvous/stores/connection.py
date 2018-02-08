from tandem.shared.stores.base import ModelBase, StoreBase


class Connection(ModelBase):
    def __init__(self, public_address, private_address=None):
        self._public_address = public_address
        self._private_address = private_address

    def __eq__(self, other):
        return self._public_address == other._public_address and \
            self._private_address == other._private_address

    def get_address(self):
        return self.get_public_address()

    def get_public_address(self):
        return self._public_address

    def get_private_address(self):
        return self._private_address


class ConnectionStore(StoreBase):
    def __init__(self):
        self._connections = {}

    def get_connection(self, address):
        return self._connections.get(address, None)

    def get_connections(self, addresses):
        return [self.get_connection(address) for address in addresses]

    def register_connection(self, connection):
        self._connections[connection.get_address()] = connection
