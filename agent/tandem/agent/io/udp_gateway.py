import socket
import logging
from tandem.agent.utils.fragment import FragmentUtils
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

    def write_data(self, messages, addresses):
        if type(messages) is not list:
            messages = [messages]

        if type(addresses) is not list:
            addresses = [addresses]

        for address in addresses:
            for message in messages:
                self._send_datagrams(message, address)

    def _send_datagrams(self, message, address):
        if FragmentUtils.should_fragment(message, self._max_payload_length):
            messages = FragmentUtils.fragment(
                message,
                self._max_payload_length
            )

            return self.write_data(messages, address)

        if type(message) is str:
            message = message.encode('utf-8')

        bytes_sent = 0
        while bytes_sent < len(message):
            bytes_sent += \
                self._socket.sendto(message[bytes_sent:], address)

    def _read_datagrams(self):
        try:
            while True:
                raw_data, address = self._socket.recvfrom(4096)
                host, port = address
                logging.debug("Received data from {}:{}.".format(host, port))

                if FragmentUtils.is_fragment(raw_data):
                    FragmentUtils.defragment(
                        raw_data,
                        address,
                        self._handler_function,
                    )
                else:
                    self._handler_function(raw_data, address)
        except:
            logging.info(
                "Tandem Agent has closed the UDP gateway on port {}."
                .format(self._port),
            )
