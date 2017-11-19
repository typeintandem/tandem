from tandem.io.connection import Connection

class ConnectionManager:
    def __init__(self, connection_message_handler):
        self._connections = {}
        self._connection_message_handler = connection_message_handler

    def register_connection(self, socket, address):
        self._connections[address] = Connection(
            socket, address, self._connection_message_handler)
        self._connections[address].start()

    def get_connection(self, address):
        if address not in self._connections:
            return None
        return self._connections[address]
