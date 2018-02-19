import logging
import uuid
from tandem.agent.io.document import Document
from tandem.agent.io.std_streams import STDStreams
from tandem.agent.io.fragmented_udp_gateway import FragmentedUDPGateway
from tandem.agent.protocol.handlers.editor import EditorProtocolHandler
from tandem.agent.protocol.handlers.interagent import InteragentProtocolHandler
from tandem.agent.protocol.handlers.rendezvous import RendezvousProtocolHandler
from tandem.shared.protocol.handlers.combined_handler import CombinedProtocolHandler
from concurrent.futures import ThreadPoolExecutor


class TandemAgent:
    def __init__(self, host, port):
        self._id = uuid.uuid4()
        self._requested_host = host
        # This is the port the user specified on the command line (it can be 0)
        self._requested_port = port
        self._document = Document()
        self._std_streams = STDStreams(self._on_std_input)
        self._interagent_gateway = FragmentedUDPGateway(
            self._requested_host,
            self._requested_port,
            self._gateway_message_handler,
        )
        self._editor_protocol = EditorProtocolHandler(
            self._std_streams,
            self._interagent_gateway,
            self._document,
        )
        self._interagent_protocol = InteragentProtocolHandler(
            self._id,
            self._std_streams,
            self._interagent_gateway,
            self._document,
        )
        self._rendezvous_protocol = RendezvousProtocolHandler(
            self._interagent_gateway,
        )
        self._gateway_handlers = CombinedProtocolHandler(
            self._interagent_protocol,
            self._rendezvous_protocol,
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

    def _on_std_input(self, retrieve_data):
        # Called by _std_streams after receiving a new message from the plugin
        self._main_executor.submit(
            self._editor_protocol.handle_message,
            retrieve_data,
        )

    def _gateway_message_handler(self, retrieve_data):
        # Do not call directly - called by _interagent_gateway
        self._main_executor.submit(
            self._handle_nullable_data,
            self._gateway_handlers.handle_raw_data,
            retrieve_data,
        )

    def _handle_nullable_data(self, handler, retrieve_data):
        io_data = retrieve_data()
        if io_data is not None:
            handler(io_data.get_data(), io_data.get_address())
