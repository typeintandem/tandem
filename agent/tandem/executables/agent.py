import logging
from tandem.io.document import Document
from tandem.io.std_streams import StdStreams
from tandem.io.udp_gateway import UDPGateway
from tandem.protocol.editor.handler import EditorProtocolHandler
from tandem.protocol.interagent.handler import InteragentProtocolHandler
from concurrent.futures import ThreadPoolExecutor


class TandemAgent:
    def __init__(self, host, port):
        self._requested_host = host
        # This is the port the user specified on the command line (it can be 0)
        self._requested_port = port
        self._document = Document()
        self._std_streams = StdStreams(self._on_std_input)
        self._interagent_gateway = UDPGateway(
            self._requested_host,
            self._requested_port,
            self._on_interagent_message,
        )
        self._editor_protocol = EditorProtocolHandler(
            self._std_streams,
            self._interagent_gateway,
            self._document,
        )
        self._interagent_protocol = InteragentProtocolHandler(
            self._std_streams,
            self._interagent_gateway,
            self._document,
        )
        self._main_executor = ThreadPoolExecutor(max_workers=1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._document.start()
        self._std_streams.start()
        self._interagent_gateway.start()
        logging.info("Tandem Agent has started.")

    def stop(self):
        def atomic_shutdown():
            self._interagent_protocol.stop()
            self._interagent_gateway.stop()
            self._std_streams.stop()
            self._document.stop()
        self._main_executor.submit(atomic_shutdown)
        self._main_executor.shutdown()
        logging.info("Tandem Agent has shut down.")

    def _on_std_input(self, data):
        # Called by _std_streams after receiving a new message from the plugin
        self._main_executor.submit(self._editor_protocol.handle_message, data)

    def _on_interagent_message(self, data, address):
        # Do not call directly - called by _interagent_gateway
        self._main_executor.submit(
            self._interagent_protocol.handle_message,
            data,
            address,
        )
