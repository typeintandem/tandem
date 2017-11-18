import sys
import threading

class StdStreamsHandler:
    def __init__(self, processor):
        self._thread = threading.Thread(target=self._stdin_read_loop)
        self._processor = processor

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.stop()

    def _stdin_read_loop(self):
        while True:
            line = sys.stdin.readline()
            if line == "":
                break
            response = self._processor.handle(line)
            sys.stdout.write(response)
            sys.stdout.write("\n")
