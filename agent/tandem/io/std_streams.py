import sys
import logging
from concurrent.futures import ThreadPoolExecutor

class StdStreams:
    def __init__(self, handler_function):
        self._handler_function = handler_function
        self._reader = ThreadPoolExecutor(max_workers=1)

    def start(self):
        self._reader.submit(self._stdin_read)

    def stop(self):
        self._reader.shutdown()
        sys.stdout.close()

    def write(self, data):
        sys.stdout.write(data)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _stdin_read(self):
        # Do not call directly - only invoked by the _reader executor
        try:
            for line in sys.stdin:
                self._handler_function(line)
        except:
            logging.exception("Exception when reading from stdin:")
            raise
