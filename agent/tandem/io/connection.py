import logging
from threading import Thread

ENCODING = "utf-8"
ENCODED_NEWLINE = "\n".encode(ENCODING)


class Connection:
    def __init__(self, socket, address, handler_function):
        self.address = address
        self._socket = socket
        self._reader = Thread(target=self._socket_read)
        self._handler_function = handler_function

    def start(self):
        self._reader.start()

    def stop(self):
        self._socket.close()
        self._reader.join()

    def write(self, string_data):
        self._socket.sendall(string_data.encode(ENCODING))
        self._socket.sendall(ENCODED_NEWLINE)

    def _socket_read(self):
        buffer = ""
        try:
            while True:
                data = self._socket.recv(4096)
                buffer += data.decode(ENCODING)
                while buffer.find("\n") != -1:
                    line, buffer = buffer.split("\n", 1)
                    self._handler_function(line, self.address)
        except:
            logging.info("Connection stopping...")
