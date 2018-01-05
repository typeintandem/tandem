import logging
from threading import Thread

ENCODING = "utf-8"
ENCODED_NEWLINE = "\n".encode(ENCODING)


class Connection:
    """
    Manages an open connection to another agent.

    This class must be constructed with an already-connected
    socket. Upon receipt of a message on the socket, the
    handler_function will be called with the raw message.

    Socket communication is in UTF-8 encoded strings with
    messages separated by newline characters.

    The stop function must be called to close the connection.
    """
    def __init__(self, socket, address, handler_function):
        self.address = address
        self._socket = socket
        self._reader = self._get_read_thread()
        self._handler_function = handler_function

    def start(self):
        self._reader.start()

    def stop(self):
        self._socket.close()
        self._reader.join()

    def write_string_message(self, string_message):
        self._socket.sendall(string_message.encode(ENCODING))
        self._socket.sendall(ENCODED_NEWLINE)

    def _get_read_thread(self):
        def socket_read():
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

        return Thread(target=socket_read)
