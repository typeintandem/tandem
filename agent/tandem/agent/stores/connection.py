from tandem.shared.stores.base import StoreBase
from tandem.agent.models.connection_state import ConnectionState


class ConnectionStore(StoreBase):
    def __init__(self):
        self._connections = {}

    def add_connection(self, connection):
        self._connections[connection.get_id()] = connection

    def remove_connection(self, connection):
        del self._connections[connection.get_id()]

    def get_connection_by_id(self, id):
        return self._connections.get(id, None)

    def get_connection_by_address(self, address):
        for _, connection in self._connections.items():
            if connection.get_active_address() == address:
                return connection
        return None

    def get_open_connections(self):
        return [
            connection for _, connection in self._connections.items()
            if (
                connection.get_connection_state() == ConnectionState.OPEN or
                connection.get_connection_state() == ConnectionState.RELAY
            )
        ]
