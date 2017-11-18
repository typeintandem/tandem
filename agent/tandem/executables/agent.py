from tandem.io.std_streams import StdStreams
from tandem.protocol.editor.handler import EditorProtocolHandler
from concurrent.futures import ThreadPoolExecutor


class TandemAgent:
    def __init__(self):
        self._std_streams = StdStreams(self._on_std_input)
        self._editor_protocol = EditorProtocolHandler(self._std_streams)
        self._main_executor = ThreadPoolExecutor(max_workers=1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._std_streams.start()

    def stop(self):
        self._std_streams.stop()
        self._main_executor.shutdown()

    def _on_std_input(self, data):
        # Do not call directly - called by _std_streams
        self._main_executor.submit(self._editor_protocol.handle, data)
