import socket
import logging
from threading import Thread


class ConnectionAcceptor:
    def __init__(self, host, port, handler_function):
        self._host = host
        self._port = port
        self._server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self._acceptor = Thread(target=self._accept_connections)
        self._handler_function = handler_function

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.stop()

    def start(self):
        self._server_socket.bind((self._host, self._port))
        self._port = self._server_socket.getsockname()[1]
        self._server_socket.listen()
        self._acceptor.start()
        logging.info(
            "Tandem Agent is listening for connections on {}:{}."
            .format(self._host, self._port),
        )

    def stop(self):
        self._server_socket.close()
        self._acceptor.join()

    def _accept_connections(self):
        # Do not call directly - only invoked by the _acceptor thread
        try:
            while True:
                socket, address = self._server_socket.accept()
                host, port = address
                logging.info(
                    "Accepted a connection to {}:{}."
                    .format(host, port),
                )
                self._handler_function(socket, address)
        except:
            logging.info("Tandem Agent has stopped accepting connections.")
