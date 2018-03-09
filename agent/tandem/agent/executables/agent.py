import logging
import uuid
from tandem.agent.io.document import Document
from tandem.agent.io.std_streams import STDStreams
from tandem.shared.io.udp_gateway import UDPGateway
from tandem.agent.protocol.handlers.editor import EditorProtocolHandler
from tandem.agent.protocol.handlers.interagent import InteragentProtocolHandler
from tandem.agent.protocol.handlers.rendezvous import RendezvousProtocolHandler
from tandem.shared.protocol.handlers.multi import MultiProtocolHandler
from tandem.shared.utils.time_scheduler import TimeScheduler
from tandem.shared.io.proxies.fragment import FragmentProxy
from tandem.shared.io.proxies.list_parameters import ListParametersProxy
from tandem.shared.io.proxies.unicode import UnicodeProxy
from tandem.shared.io.proxies.reliability import ReliabilityProxy
from tandem.agent.io.proxies.relay import AgentRelayProxy
from concurrent.futures import ThreadPoolExecutor
from tandem.agent.configuration import RENDEZVOUS_ADDRESS


class TandemAgent:
    def __init__(self, host, port):
        self._id = uuid.uuid4()
        self._requested_host = host
        # This is the port the user specified on the command line (it can be 0)
        self._requested_port = port
        self._main_executor = ThreadPoolExecutor(max_workers=1)
        self._time_scheduler = TimeScheduler(self._main_executor)
        self._document = Document()
        self._std_streams = STDStreams(self._on_std_input)
        self._interagent_gateway = UDPGateway(
            self._requested_host,
            self._requested_port,
            self._gateway_message_handler,
            [
                ListParametersProxy(),
                UnicodeProxy(),
                FragmentProxy(),
                AgentRelayProxy(RENDEZVOUS_ADDRESS),
                ReliabilityProxy(self._time_scheduler),
            ],
        )
        self._editor_protocol = EditorProtocolHandler(
            self._id,
            self._std_streams,
            self._interagent_gateway,
            self._document,
        )
        self._interagent_protocol = InteragentProtocolHandler(
            self._id,
            self._std_streams,
            self._interagent_gateway,
            self._document,
            self._time_scheduler,
        )
        self._rendezvous_protocol = RendezvousProtocolHandler(
            self._id,
            self._interagent_gateway,
            self._time_scheduler,
            self._document,
        )
        self._gateway_handlers = MultiProtocolHandler(
            self._interagent_protocol,
            self._rendezvous_protocol,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._time_scheduler.start()
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
            self._time_scheduler.stop()
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
            self._gateway_handlers.handle_raw_data,
            retrieve_data,
        )
