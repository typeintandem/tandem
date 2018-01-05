import sys
import logging
from threading import Thread


class StdStreams:
    def __init__(self, handler_function):
        self._handler_function = handler_function
        self._reader = self._get_read_thread()

    def start(self):
        self._reader.start()

    def stop(self):
        self._reader.join()
        sys.stdout.close()

    def write(self, data):
        sys.stdout.write(data)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _get_read_thread(self):
        def stdin_read():
            try:
                for line in sys.stdin:
                    self._handler_function(line)
            except:
                logging.exception("Exception when reading from stdin:")
                raise
        return Thread(target=stdin_read)
