import socket
from concurrent.futures import ThreadPoolExecutor

class ConnectionAcceptor:
    def __init__(self, port, handler_function):
        self._port = port
        self._server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self._accept_executor = ThreadPoolExecutor(max_workers=1)
        self._handler_function = handler_function

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.stop()

    def start(self):
        self._server_socket.bind(("", self._port))
        self._server_socket.listen()
        self._accept_executor.submit(self._accept_connections)

    def stop(self):
        self._server_socket.close()
        self._accept_executor.shutdown()

    def _accept_connections(self):
        while True:
            socket, address = self._server_socket.accept()
            self._handler_function(socket, address)
