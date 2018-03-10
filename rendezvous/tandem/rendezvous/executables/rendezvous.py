import logging
from tandem.shared.io.udp_gateway import UDPGateway
from tandem.shared.io.proxies.fragment import FragmentProxy
from tandem.shared.io.proxies.list_parameters import ListParametersProxy
from tandem.shared.io.proxies.unicode import UnicodeProxy
from tandem.rendezvous.io.proxies.relay import RendezvousRelayProxy
from tandem.shared.io.proxies.reliability import ReliabilityProxy
from tandem.rendezvous.protocol.handlers.agent import (
    AgentRendezvousProtocolHandler
)
from tandem.shared.utils.time_scheduler import TimeScheduler
from concurrent.futures import ThreadPoolExecutor


class TandemRendezvous(object):
    def __init__(self, host, port):
        self._main_executor = ThreadPoolExecutor(max_workers=1)
        self._time_scheduler = TimeScheduler(self._main_executor)
        self._udp_gateway = UDPGateway(
            host,
            port,
            self._on_receive_message,
            [
                ListParametersProxy(),
                UnicodeProxy(),
                FragmentProxy(),
                RendezvousRelayProxy(),
                ReliabilityProxy(self._time_scheduler),
            ],
        )
        self._rendezvous_protocol = AgentRendezvousProtocolHandler(
            self._udp_gateway,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._udp_gateway.start()
        logging.info("Tandem Rendezvous has started.")

    def stop(self):
        self._udp_gateway.stop()
        self._main_executor.shutdown()
        logging.info("Tandem Rendezvous has shut down.")

    def _on_receive_message(self, retrieve_data):
        self._main_executor.submit(
            self._rendezvous_protocol.handle_raw_data,
            retrieve_data,
        )
