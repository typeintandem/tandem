import sys
import logging
from threading import Thread


class StdStreams:
    def __init__(self, handler_function):
        self._handler_function = handler_function
        self._reader = Thread(target=self._stdin_read)

    def start(self):
        self._reader.start()

    def stop(self):
        self._reader.join()
        sys.stdout.close()

    def write_string_message(self, string_message):
        sys.stdout.write(string_message)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _stdin_read(self):
        try:
            for line in sys.stdin:
                self._handler_function(line)
        except:
            logging.exception("Exception when reading from stdin:")
            raise
