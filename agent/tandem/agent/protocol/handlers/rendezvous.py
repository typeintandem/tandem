import logging
import uuid
from tandem.agent.models.pinging_peer import PingingPeer
from tandem.agent.stores.pinging_peer import PingingPeerStore
from tandem.shared.protocol.handlers.base import ProtocolHandlerBase
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    RendezvousProtocolMessageType,
)
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    Ping,
)
from tandem.agent.utils.hole_punching import HolePunchingUtils
from tandem.shared.utils.static_value import static_value as staticvalue


class RendezvousProtocolHandler(ProtocolHandlerBase):
    @staticvalue
    def _protocol_message_utils(self):
        return RendezvousProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            RendezvousProtocolMessageType.SetupParameters.value:
                self._handle_setup_parameters,
            RendezvousProtocolMessageType.Error.value:
                self._handle_error,
        }

    def __init__(self, id, gateway, time_scheduler):
        self._id = id
        self._gateway = gateway
        self._time_scheduler = time_scheduler

    def _handle_setup_parameters(self, message, sender_address):
        logging.debug("Received SetupParameters - connect to: {}".format(message.peer_id))
        new_peer = PingingPeer(
            id=uuid.UUID(message.peer_id),
            addresses=[
                (peer_info[0], peer_info[1])
                for peer_info in message.connect_to
            ],
            initiated_connection=message.initiate,
        )
        pinging_peer_store = PingingPeerStore.get_instance()
        pinging_peer_store.add_peer(new_peer)

        ping_handle = self._time_scheduler.run_every(
            HolePunchingUtils.PING_INTERVAL,
            HolePunchingUtils.send_ping,
            self._gateway,
            new_peer,
            self._id,
        )
        new_peer.set_ping_handle(ping_handle)


    def _handle_error(self, message, sender_address):
        logging.info("Rendezvous Error: {}".format(message.message))
