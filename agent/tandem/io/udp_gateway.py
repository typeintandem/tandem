import socket
import logging
from threading import Thread


class UDPGateway:
    def __init__(self, host, port, handler_function, max_payload_length=512):
        self._host = host
        self._port = port
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )
        self._reader = Thread(target=self._read_datagrams)
        self._handler_function = handler_function
        self._max_payload_length = max_payload_length

    def start(self):
        self._socket.bind((self._host, self._port))
        self._reader.start()

    def stop(self):
        self._socket.close()
        self._reader.join()

    def write_binary_data(self, binary_data, address):
        bytes_sent = 0
        while bytes_sent < len(binary_data):
            bytes_sent += \
                self._socket.sendto(binary_data[bytes_sent:], address)

    def max_payload_length(self):
        return self._max_payload_length

    def split_payload(self, binary_payload, header_length=0):
        max_payload_length = self._max_payload_length - header_length
        return [
            binary_payload[i:i + max_payload_length]
            for i in range(0, len(binary_payload), max_payload_length)
        ]

    def _read_datagrams(self):
        try:
            while True:
                raw_data, address = self._socket.recvfrom(4096)
                host, port = address
                logging.debug("Received data from {}:{}.".format(host, port))
                self._handler_function(raw_data, address)
        except:
            logging.info(
                "Tandem Agent has closed the UDP gateway on port {}."
                .format(self._port),
            )
