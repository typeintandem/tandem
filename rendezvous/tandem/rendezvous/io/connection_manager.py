import socket
import logging
from threading import Thread


class ConnectionManager:
    def __init__(self, host, port, handler_function):
        self._host = host
        self._port = port
        self._socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._handler_function = handler_function
        self._acceptor = Thread(target=self._handle_receive)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.stop()

    def start(self):
        self._socket_server.bind((self._host, self._port))
        self._acceptor.start()
        logging.info("Tandem Rendezvous is listening on {}.".format((
            self._host,
            self._port
        )))

    def stop(self):
        self._socket_server.close()
        self._acceptor.join()

    def send_data(self, address, data):
        logging.info("Sending data {} to {}" .format(
            data,
            address,
        ))
        binary_data = data.encode("utf-8")
        bytes_sent = 0
        while bytes_sent < len(binary_data):
            bytes_sent += self._socket_server.sendto(
                binary_data[bytes_sent:],
                address,
            )

    def _handle_receive(self):
        try:
            while True:
                data, address = self._socket_server.recvfrom(4096)
                logging.info("Received data {} from {}" .format(data, address))
                self._handler_function(data, address)
        except:
            logging.info(
                "Tandem Rendezvous has stopped accepting connections."
            )
