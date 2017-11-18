from tandem.io.std_streams_handler import StdStreamsHandler
from tandem.handlers.client_protocol import ClientProtocolHandler


class TandemAgent:
    def __init__(self):
        self._client_protocol_handler = ClientProtocolHandler()
        self._std_streams = StdStreamsHandler(self._client_protocol_handler)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._std_streams.start()

    def stop(self):
        self._std_streams.stop()
