import sys
import logging
from concurrent.futures import ThreadPoolExecutor

class StdStreams:
    def __init__(self, handler_function):
        self._shutting_down = False
        self._handler_function = handler_function
        self._reader = ThreadPoolExecutor(max_workers=1)
        self._writer = ThreadPoolExecutor(max_workers=1)

    def start(self):
        if self._shutting_down:
            return
        self._reader.submit(self._stdin_read)

    def stop(self):
        self._shutting_down = True
        self._reader.shutdown()
        self._writer.shutdown()
        sys.stdout.close()

    def write(self, data):
        if self._shutting_down:
            return
        self._writer.submit(self._stdout_write, data)

    def _stdout_write(self, data):
        # Do not call directly - only invoked by the _writer executor
        try:
            sys.stdout.write(data)
            sys.stdout.write("\n")
            sys.stdout.flush()
        except:
            logging.exception("Exception when writing data to stdout:")
            raise

    def _stdin_read(self):
        # Do not call directly - only invoked by the _reader executor
        try:
            for line in sys.stdin:
                self._handler_function(line)
        except:
            logging.exception("Exception when reading from stdin:")
            raise
