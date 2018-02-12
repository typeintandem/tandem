from tandem.shared.models.base import ModelBase
from tandem.rendezvous.stores.connection import ConnectionStore


class Session(ModelBase):
    def __init__(self, uuid):
        self._connections = []
        self._uuid = uuid

    def add_connection(self, connection):
        self._connections.append(connection.get_address())

    def remove_connection(self, connection):
        self._connections.remove(connection.get_address())

    def get_connections(self):
        return ConnectionStore.get_instance().get_connections(
            self._connections
        )
