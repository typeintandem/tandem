import socket
from tandem.io.connection import Connection


class ConnectionManager:
    def __init__(self, connection_message_handler):
        self._connections = {}
        self._connection_message_handler = connection_message_handler

    def register_connection(self, opened_socket, address):
        self._connections[address] = Connection(
            opened_socket, address, self._connection_message_handler)
        self._connections[address].start()

    def get_connection(self, address):
        if address not in self._connections:
            return None
        return self._connections[address]

    def connect_to(self, host, port):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((host, port))
        self.register_connection(new_socket, (host, port))

    def stop(self):
        for _, connection in self._connections.items():
            connection.stop()
