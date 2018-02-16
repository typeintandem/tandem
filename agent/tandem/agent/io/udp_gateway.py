import socket
import logging
from tandem.agent.io.base import InterfaceDataBase, InterfaceBase


class UDPData(InterfaceDataBase):
    def __init__(self, raw_data, address):
        super(UDPData, self).__init__(raw_data)
        self._address = address

    def get_address(self):
        return self._address


class UDPGateway(InterfaceBase):
    def __init__(self, host, port, handler_function):
        super(UDPGateway, self).__init__(handler_function)
        self._host = host
        self._port = port
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

    def start(self):
        self._socket.bind((self._host, self._port))
        super(UDPGateway, self).start()

    def stop(self):
        self._socket.close()
        super(UDPGateway, self).stop()

    def generate_io_data(self, messages, addresses):
        if type(messages) is not list:
            messages = [messages]

        if type(addresses) is not list:
            addresses = [addresses]

        data = []
        for address in addresses:
            for message in messages:
                if type(message) is str:
                    message = message.encode("utf-8")
                data.append(UDPData(message, address))

        return data

    def write_io_data(self, io_datas):
        if type(io_datas) is not list:
            io_datas = [io_datas]

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
        try:
            while True:
                raw_data, address = self._socket.recvfrom(4096)
                host, port = address
                logging.debug("Received data from {}:{}.".format(host, port))
                self._received_data(UDPData(raw_data, address))
        except:
            logging.info(
                "Tandem Agent has closed the UDP gateway on port {}."
                .format(self._port),
            )
