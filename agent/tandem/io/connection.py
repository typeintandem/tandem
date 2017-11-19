import logging
from concurrent.futures import ThreadPoolExecutor

class Connection:
    def __init__(self, socket, address, handler_function):
        self._socket = socket
        self._buffered_socket = socket.makefile(mode="w", encoding="utf-8")
        self._address = address
        self._reader = ThreadPoolExecutor(max_workers=1)
        self._handler_function = handler_function

    def start(self):
        self._reader.submit(self._socket_read)

    def stop(self):
        self._socket.close()
        self._reader.shutdown()

    def write(self, data):
        self._buffered_socket.write(data)
        self._buffered_socket.write("\n")
        self._buffered_socket.flush()

    def _socket_read(self):
        try:
            for line in self._buffered_socket:
                self._handler_function(line, self._address)
        except:
            logging.exception("Exception when reading from connection:")
            raise
