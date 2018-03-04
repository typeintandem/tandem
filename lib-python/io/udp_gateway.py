import select
import socket
import logging
from tandem.shared.io.base import InterfaceDataBase, InterfaceBase


class UDPData(InterfaceDataBase):
    def __init__(self, raw_data, address):
        super(UDPData, self).__init__(raw_data)
        self._address = address

    def get_address(self):
        return self._address

    def is_empty(self):
        return self._data is None and self._address is None


class UDPGateway(InterfaceBase):
    data_class = UDPData
    SELECT_TIMEOUT = 0.5

    def __init__(self, host, port, handler_function, proxies=[]):
        super(UDPGateway, self).__init__(handler_function, proxies)
        self._host = host
        self._port = port
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )
        self._shutdown_requested = False

    def start(self):
        self._socket.bind((self._host, self._port))
        super(UDPGateway, self).start()
        logging.info("Tandem UDPGateway is listening on {}.".format((
            self._host,
            self._port,
        )))

    def stop(self):
        self._shutdown_requested = True
        # We need to ensure the reader thread has been joined before closing
        # the socket to make sure we don't call select() on an invalid file
        # descriptor.
        super(UDPGateway, self).stop()
        self._socket.close()

    def get_port(self):
        return self._socket.getsockname()[1]

    def _generate_io_data(self, *args, **kwargs):
        messages, addresses = args

        data = []
        for address in addresses:
            for message in messages:
                data.append(UDPData(message, address))

        return data

    def _write_io_data(self, *args, **kwargs):
        io_datas, = args

        for io_data in io_datas:
            message = io_data.get_data()
            address = io_data.get_address()
            bytes_sent = 0

            while bytes_sent < len(message):
                bytes_sent += self._socket.sendto(
                    message[bytes_sent:],
                    address
                )

    def _read_data(self):
        while not self._shutdown_requested:
            ready_to_read, _, _ = select.select(
                [self._socket],
                [],
                [],
                UDPGateway.SELECT_TIMEOUT,
            )
            if len(ready_to_read) == 0:
                # If no descriptors are ready to read, it means the select()
                # call timed out. So check if we should exit and, if not, wait
                # for data again.
                continue

            raw_data, address = self._socket.recvfrom(4096)
            logging.debug("Received data from {}:{}.".format(*address))
            self._received_data(raw_data, address)

        logging.info(
            "Tandem has closed the UDP gateway on port {}."
            .format(self._port),
        )
