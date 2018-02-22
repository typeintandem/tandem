import logging
import uuid
from tandem.agent.models.connection import HolePunchedConnection
from tandem.agent.stores.connection import ConnectionStore
from tandem.agent.utils.hole_punching import HolePunchingUtils
from tandem.shared.models.peer import Peer
from tandem.shared.protocol.handlers.base import ProtocolHandlerBase
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    RendezvousProtocolMessageType,
)
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
        public_address = (message.public[0], message.public[1])
        private_address = (message.private[0], message.private[1])
        logging.debug(
            "Received SetupParameters - Connect to {} at public {}:{} "
            "and private {}:{}"
            .format(message.peer_id, *public_address, *private_address),
        )
        peer = Peer(
            id=uuid.UUID(message.peer_id),
            public_address=public_address,
            private_address=private_address,
        )
        new_connection = HolePunchedConnection(
            peer=peer,
            initiated_connection=message.initiate,
        )
        new_connection.set_interval_handle(self._time_scheduler.run_every(
            HolePunchingUtils.PING_INTERVAL,
            HolePunchingUtils.send_ping,
            self._gateway,
            peer.get_addresses(),
            self._id,
        ))
        ConnectionStore.get_instance().add_connection(new_connection)

    def _handle_error(self, message, sender_address):
        logging.info("Rendezvous Error: {}".format(message.message))
