import logging
from threading import Thread

class Connection:
    def __init__(self, socket, address, handler_function):
        self._socket = socket
        self._buffered_socket = socket.makefile(mode="w", encoding="utf-8")
        self._address = address
        self._reader = Thread(target=self._socket_read)
        self._handler_function = handler_function

    def start(self):
        self._reader.start()

    def stop(self):
        self._socket.close()
        self._reader.join()

    def write(self, data):
        self._buffered_socket.write(data)
        self._buffered_socket.write("\n")
        self._buffered_socket.flush()

    def _socket_read(self):
        # Do not invoke directly - only invoked by the _reader thread
        try:
            for line in self._buffered_socket:
                self._handler_function(line, self._address)
        except:
            logging.exception("Exception when reading from connection:")
            raise
