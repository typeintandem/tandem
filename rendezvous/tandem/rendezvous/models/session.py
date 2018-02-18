from tandem.shared.models.base import ModelBase


class Session(ModelBase):
    def __init__(self, session_id):
        self._connections = {}
        self._session_id = session_id

    def add_connection(self, connection):
        self._connections[connection.get_id()] = connection

    def remove_connection(self, connection):
        del self._connections[connection.get_id()]

    def get_connection(self, id):
        self._connections.get(id, None)

    def get_connections(self):
        return [connection for _, connection in self._connections.items()]
