import logging
from tandem.rendezvous.io.connection_manager import ConnectionManager
from tandem.rendezvous.protocol.handler.agent import AgentRendezvousProtocolHandler
from concurrent.futures import ThreadPoolExecutor


class TandemRendezvous(object):
    def __init__(self, host, port):
        self._connection_manager = ConnectionManager(host, port, self._on_receive_message)
        self._rendezvous_protocol = AgentRendezvousProtocolHandler(self._connection_manager)
        self._main_executor = ThreadPoolExecutor(max_workers=1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._connection_manager.start()
        logging.info("Tandem Rendezvous has started.")

    def stop(self):
        self._connection_manager.stop()
        self._main_executor.shutdown()
        logging.info("Tandem Rendezvous has shut down.")

    def _on_receive_message(self, data, address):
        self._main_executor.submit(
            self._rendezvous_protocol.handle_message,
            data,
            address,
        )
